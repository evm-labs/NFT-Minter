from gas import set_gas_limit, set_base, calculate_gas_max, set_gas_tip, calculate_final_tx_fee
from config import EXPECTED_SALE_PER_UNIT, DESIRED_RETURN, MINT_PRICE_PER_UNIT, \
                    UNITS, WALLET, RECIPIENT_ADDRESS, MINT_FUNCTION, CHAIN, MINT_FUNCTION_ARGUMENTS, Web3Instance, \
                    RELEASE_FUNCTION, RELEASE_FUNCTION_ARGUMENTS
from constants import WEI_TO_GWEI, ETH_TO_GWEI, BLOXROUTE_CERTIFICATION_DIRECTORY, BLOXROUTE_WSS_PORT
from secrets import WALLETS, BLOXROUTE_AUTH_HEADER
import time, datetime, sha3, asyncio
from bloxroute_cli.provider.cloud_wss_provider import CloudWssProvider
from bloxroute_cli.provider.ws_provider import WsProvider
from bxcommon.rpc.rpc_request_type import RpcRequestType


def encode_input_data(function: str, args: list):  # For function, pass in only variables types and no whitespace
    k = sha3.keccak_256()
    k.update(function.encode('utf-8'))
    method_id = '0x' + k.hexdigest()[0:8]
    encoded_data = method_id
    for arg in args:
        if type(arg) == int:
            arg = hex(arg)[2:]  # strip 0x
        if type(arg) == bool:
            arg = hex(int(arg))
        if type(arg) == str:
            if arg[0:2] == '0x':
                arg = arg[2:]
        new_input = arg.zfill(64)
        encoded_data += new_input
    return encoded_data


def generate_snipe_tx():
    GAS_LIMIT = set_gas_limit()
    BASE = set_base()  # return in gwei
    TIP = set_gas_tip(EXPECTED_SALE_PER_UNIT, DESIRED_RETURN, GAS_LIMIT, BASE, MINT_PRICE_PER_UNIT, UNITS)  #
    MAX = calculate_gas_max(BASE, TIP)
    INPUT_DATA = encode_input_data(MINT_FUNCTION, MINT_FUNCTION_ARGUMENTS)
    print("Mint function and arguments below:")
    print(MINT_FUNCTION, " ", MINT_FUNCTION_ARGUMENTS)
    print("Input Data hash created:")
    print(INPUT_DATA)
    print("Proceed? (y/n)")
    proceed = input()
    tx, tx_error = None, None
    if proceed == 'n':
        raise RuntimeError("Incorrect hash - interrupting run. Transaction not sent.")
    try:
        nonce = Web3Instance.eth.getTransactionCount(WALLETS[WALLET]['public'])
        tx = {
            'nonce': nonce,
            'to': RECIPIENT_ADDRESS,
            'value': Web3Instance.toWei(MINT_PRICE_PER_UNIT * UNITS, 'gwei'),
            'gas': GAS_LIMIT,
            'maxPriorityFeePerGas': Web3Instance.toWei(TIP, 'gwei'),
            'maxFeePerGas': Web3Instance.toWei(MAX, 'gwei'),
            'chainId': CHAIN,
            'data': INPUT_DATA
        }
    except:
        tx_error = "Failed to generate transaction."
    return tx, nonce, tx_error


def sign_tx(tx, private_key):
    signature_error_catcher, tx_signed = None, None
    try:
        tx_signed = Web3Instance.eth.account.sign_transaction(tx, private_key)
        tx_signed = tx_signed.rawTransaction.hex()[2:]
    except:
        signature_error_catcher = "Failed to sign transaction"
    # Error catcher
    return tx_signed, signature_error_catcher


async def send_tx(signed_tx):
    send_error_catcher, sent_tx = None, None
    listening_input_data, listening_recipient = variables_for_listening()  # generate variables for listening
    try:
        async with WsProvider(
                uri="wss://api.blxrbdn.com/ws",  # When using Gateway, change to uri="ws://127.0.0.1:28333"
                headers={"Authorization": BLOXROUTE_AUTH_HEADER},
        ) as ws_send:

            # listen and release when match
            await listen_and_release(listening_input_data, listening_recipient)

            sent_tx = await ws_send.call_bx(RpcRequestType.BLXR_TX, {"transaction": signed_tx})
    except:
        send_error_catcher = "Failed to send transaction"
    return sent_tx, send_error_catcher


def get_receipt(tx_hash):
    flag = True
    increment = 0
    tx_receipt = None
    nonce = Web3Instance.eth.getTransactionCount(WALLETS[WALLET]['public'])
    time.sleep(10)
    tx_fee = None
    while flag:
        try:
            tx_receipt = Web3Instance.eth.getTransactionReceipt(tx_hash)
            flag = False
            nonce = Web3Instance.eth.getTransactionCount(WALLETS[WALLET]['public'])
            tx_fee = calculate_final_tx_fee(tx_receipt)
        except:
            time.sleep(1)
            increment += 1
            if increment > 35:
                flag = False
    return tx_receipt, nonce, tx_fee


def variables_for_listening():
    data_hash_of_tx = encode_input_data(RELEASE_FUNCTION, RELEASE_FUNCTION_ARGUMENTS)
    address_from = RECIPIENT_ADDRESS
    return data_hash_of_tx, address_from


async def run(input_to_listen, recipient_to_listen):
    async with CloudWssProvider(
            ssl_dir=BLOXROUTE_CERTIFICATION_DIRECTORY,
            ws_uri=BLOXROUTE_WSS_PORT
    ) as ws_listen:
        subscription_id = await ws_listen.subscribe("newTxs", {"include": ["tx_hash", "tx_contents"]})
        start = time.time()

        flag = True
        print(f'Started listening at {datetime.datetime.now()}')
        print(f"Listening for a transaction with this recipient {recipient_to_listen} and this input {input_to_listen}.")

        while flag:

            next_notification = await ws_listen.get_next_subscription_notification_by_id(subscription_id)

            tx_recipient = next_notification.notification["txContents"]["to"]
            tx_input = next_notification.notification["txContents"]["input"]
            if input_to_listen == tx_input and tx_recipient == recipient_to_listen:
                flag = False
            if time.time() - start > 5:  # Comment this out if in prod
                flag = False
            time.sleep(1)
        await ws_listen.unsubscribe(subscription_id)


async def listen_and_release(input_to_listen, recipient_to_listen):

    await run(input_to_listen, recipient_to_listen)

