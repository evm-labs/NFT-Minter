from gas import set_gas_limit, set_base, calculate_gas_max, set_gas_tip
from config import EXPECTED_SALE_PER_UNIT, DESIRED_RETURN, MINT_PRICE_PER_UNIT, \
                    UNITS, WALLET, RECIPIENT_ADDRESS, MINT_FUNCTION, CHAIN, Web3Instance
from constants import WEI_TO_GWEI, ETH_TO_GWEI, MAINNET_ID, RINKEBY_ID
from secrets import WALLETS
import time


def generate_transact_tx():
    GAS_LIMIT = 21000
    BASE = 80 # set_base()  # return in gwei
    TIP = 40  # get tip from https://etherscan.io/gastracker
    MAX = calculate_gas_max(BASE, TIP)
    VALUE = 0.01
    tx, tx_error = None, None

    try:

        nonce = Web3Instance.eth.getTransactionCount(WALLETS[WALLET]['public'])

        tx = {
            'nonce': nonce,
            'to': RECIPIENT_ADDRESS,
            'value': Web3Instance.toWei(VALUE, 'ether'),
            'gas': GAS_LIMIT,
            'maxPriorityFeePerGas': Web3Instance.toWei(TIP, 'gwei'),
            'maxFeePerGas': Web3Instance.toWei(MAX, 'gwei'),
            'chainId': CHAIN,
        }

    except:
        tx_error = "Failed to generate transaction."

    return tx, nonce, tx_error
