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
from snipe_setup import variables_for_listening
import nest_asyncio


# async def run(input_to_listen, recipient_to_listen, break_clause=True):
#     async with CloudWssProvider(
#             ssl_dir=BLOXROUTE_CERTIFICATION_DIRECTORY,
#             ws_uri=BLOXROUTE_WSS_PORT
#     ) as ws:
#         subscription_id = await ws.subscribe("newTxs", {"include": ["tx_hash", "tx_contents"]})
#
#         flag = True
#         print(f'Started listening at {datetime.datetime.now()}')
#         start = time.time()
#
#         while flag:
#
#             next_notification = await ws.get_next_subscription_notification_by_id(subscription_id)
#
#             tx_recipient = next_notification.notification["txContents"]["to"]
#             tx_input = next_notification.notification["txContents"]["input"]
#             if input_to_listen == tx_input and tx_recipient == recipient_to_listen:
#                 flag = False
#             if time.time() - start > 6:
#                 flag = False
#             time.sleep(3)
#             print(time.time())
#         await ws.unsubscribe(subscription_id)
#
#
# async def listen_and_release(input_to_listen, recipient_to_listen):
#     await run(input_to_listen, recipient_to_listen)
#     # loop = asyncio.get_event_loop()
#     # loop.run_until_complete(await asyncio.gather(run(input_to_listen, recipient_to_listen)))
#     # loop.close()
#
#
# listening_input_data, listening_recipient = variables_for_listening()
# asyncio.run(listen_and_release(listening_input_data, listening_recipient))


def generate_snipe_tx():
    GAS_LIMIT = 21000
    BASE = 40  # return in gwei
    TIP = 1
    MAX = 100
    tx, tx_error = None, None
    try:
        nonce = Web3Instance.eth.getTransactionCount(WALLETS[WALLET]['public'])
        tx = {
            'nonce': nonce,
            'to': '0x7Bc6f01115F4b0Db6771FEd332B3380C7b840F2C',
            'value': 0,
            'gas': GAS_LIMIT,
            'maxPriorityFeePerGas': Web3Instance.toWei(TIP, 'gwei'),
            'maxFeePerGas': Web3Instance.toWei(MAX, 'gwei'),
            'chainId': CHAIN,
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
    async with WsProvider(
            uri="wss://api.blxrbdn.com/ws",  # When using Gateway, change to uri="ws://127.0.0.1:28333"
            headers={"Authorization": BLOXROUTE_AUTH_HEADER},
    ) as ws_send:

        sent_tx = await ws_send.call_bx(RpcRequestType.BLXR_TX, {"transaction": signed_tx})
        print(signed_tx)
        print(sent_tx)
        tx_receipt = Web3Instance.eth.getTransactionReceipt(sent_tx.__dict__['result']['txHash'])
        print(tx_receipt)
        try:
            sent_tx = sent_tx.hex()
        except:
            pass
    # except:
    #     send_error_catcher = "Failed to send transaction"
    return sent_tx, send_error_catcher


tx, nonce, tx_error = generate_snipe_tx()
tx_signed, signature_error_catcher = sign_tx(tx, WALLETS["Account 1"]["private"])
sent_tx, send_error_catcher = asyncio.run(send_tx(tx_signed))
print(f"Transaction hash is {sent_tx.__dict__['result']['txHash']}")
