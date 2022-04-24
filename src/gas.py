from web3 import Web3
from constants import WEI_TO_GWEI, ETH_TO_GWEI
from config import CONTRACT, ESTIMATE_GAS_FUNCTION, MINT_PRICE_PER_UNIT, Web3Instance


def calculate_final_tx_fee(tx_receipt):
    final_tx_fee_eth = int(tx_receipt.__dict__["effectiveGasPrice"], 16) * \
                       tx_receipt.__dict__["gasUsed"] / WEI_TO_GWEI / ETH_TO_GWEI
    return final_tx_fee_eth


def estimate_gas_limit():
    gas_estimate = ESTIMATE_GAS_FUNCTION.estimateGas()
    return gas_estimate


def set_gas_limit():
    gas_estimate = 330000  # estimate_gas_limit()
    print(f"Gas estimate is {gas_estimate}. How do you want to set your limit?")
    gas_limit_set = input()
    return int(gas_limit_set)


def set_base():
    base_gwei = int(Web3Instance.eth.getBlock('latest').__dict__['baseFeePerGas'], 16)/WEI_TO_GWEI
    next_block_multipliers = [1, 1.125, 1*(1.125**2), 1*(1.125**3), 1*(1.125**4), 1*(1.125**5), 1*(1.125**6)]
    print("Base for next 1 + 6 blocks:")
    for i in range(len(next_block_multipliers)):
        print(f"{next_block_multipliers[i]*base_gwei}")
    print("How do you want to set your base (only used for tip calculation)?")
    base_gwei = input()
    return float(base_gwei)


def calculate_gas_max(base, tip):
    # Base and tip should be based on input unless its empty. Always clean up the input config
    max_gas = 2 * base + tip
    return max_gas


def set_gas_tip(expected_sale_per_unit, desired_return, gas_limit, base, mint_price_per_unit, units):
    # all units in GWEI
    tip_all_units = round(units*(expected_sale_per_unit - expected_sale_per_unit*desired_return - mint_price_per_unit) / gas_limit - base, 0)
    print(f'Tip calculated is equal to {tip_all_units} GWEI.')
    print("How do you want to set your tip? (provide int)")
    total_tip = int(input())
    # TODO: On the margin, this might turn negative.
    # function is: (base + tip_per_unit*units)*gas_limit + mint_price_per_unit*units = (expected_sale_per_unit*units - expected_sale_per_unit*units*desired_return)
    return total_tip
