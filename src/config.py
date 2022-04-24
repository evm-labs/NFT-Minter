import json
import requests
from constants import WEI_TO_GWEI, ETH_TO_GWEI, MAINNET_ID, RINKEBY_ID, INFURA_RINKEBY, INFURA_MAIN
from web3 import Web3
from contract import WrappedContract

# Define type of transaction
TYPE = 'Snipe'  # [Snipe, Transact]

# Wallet name
WALLET = 'Account 1'

# ID of chain to be used
NETWORK = 'MAIN'
CHAIN = MAINNET_ID
if CHAIN == RINKEBY_ID:
    Web3Instance = Web3(Web3.HTTPProvider(INFURA_RINKEBY))
else:
    Web3Instance = Web3(Web3.HTTPProvider(INFURA_MAIN))


# Address of recipient
RECIPIENT_ADDRESS = '0x4a8C9D751EEAbc5521A68FB080DD7E72E46462aF'  # Contract address for Arcade Land

##########################################
# The below lines relate to sniping NFTs #
##########################################

# Block to get contract
W_CONTRACT = WrappedContract(RECIPIENT_ADDRESS, CHAIN, NETWORK, Web3Instance)


# Block to estimate Gas Limit
CONTRACT_ABI = W_CONTRACT.get_abi_from_etherscan()
CONTRACT = W_CONTRACT.contract()
ESTIMATE_GAS_FUNCTION = 'x' # CONTRACT.functions.mintApe(1)  # .? (e.g. '.mint(4)') FOR ALL UNITS mintApe(uint numberOfTokens)

# Block to estimate Tip
EXPECTED_SALE_PER_UNIT = 0.8 * ETH_TO_GWEI
DESIRED_RETURN = 0.2
UNITS = 2
MINT_PRICE_PER_UNIT = 0 * ETH_TO_GWEI

# Block to snipe
MINT_FUNCTION = 'mintLargeLands(uint256)'  # mintStandardLands(uint256 quantity)
MINT_FUNCTION_ARGUMENTS = [2]  # mint(uint numberOfTokens) i.e. parameter values
RELEASE_TIME = 'X'
RELEASE_FUNCTION = 'flipMintState()'  # flipMintState()
RELEASE_FUNCTION_ARGUMENTS = []






