import os
from web3 import Web3
from dotenv import load_dotenv
from scripts.deploy_survey_factory_data_compute import create_nft_datatoken_compute, published_on_ocean_compute
from scripts.deploy_survey_algo import create_nft_algo, published_algo_on_ocean
from scripts.deploy_survey_vault import survey_vault
from scripts.deploy_datanft_vault import dataNft_vault
from scripts.add_to_white_list import addToWhiteList
from scripts.deploy_survey_factory import create_nft_datatoken, published_on_ocean
from scripts.approve_datanft_contract import approve_contract
from scripts.transfer_nft import transfer_nft_to_datanft_contract
from scripts.allows_algo import allowsAlgorithm
from web3.middleware import geth_poa_middleware
from ocean_lib.ocean.ocean import Ocean
# from ocean_lib.web3_internal.utils import connect_to_network
from eth_account import Account
from ocean_lib.example_config import get_config_dict
import os
# from brownie.network import accounts
load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv("MUMBAI_RPC_URL")))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
# Check if connected (should return True)
print(w3.is_connected())
# connect_to_network("polygon-test")
# print(network.is_connected())
config = get_config_dict("mumbai")
ocean = Ocean(config)

bob_pr = os.getenv('PRIVATE_KEY')
bob = w3.eth.account._parsePrivateKey(bob_pr)
print((bob))

# return nft address and token address (datatokenaddress, nftaddress)
info_address_nft_token = create_nft_datatoken_compute(w3)
info_address_nft_token_algo = create_nft_algo(w3)

#published your nft on ocean market
ddo_data = published_on_ocean_compute(w3, info_address_nft_token)
ddo_algo = published_algo_on_ocean(w3, info_address_nft_token_algo)

job_result = allowsAlgorithm(w3, ddo_data, ddo_algo, ocean)
# print(f"https://market.oceanprotocol.com/asset/{ddo_id}");
print(job_result)
ocean.assets.create_url_asset
# dataNft_contract_address = dataNft_vault(w3)
# #return address of survey vault contract
# vault_contract_address = survey_vault(w3, dataNft_contract_address)

# # return nft address and token address (datatokenaddress, nftaddress)
# info_address_nft_token = create_nft_datatoken(w3)

# #published your nft on ocean market
# ddo_id = published_on_ocean(w3, info_address_nft_token, vault_contract_address)

# print(f"https://market.oceanprotocol.com/asset/{ddo_id}");

# # w3, dataNft_contract_address, token_id, nftaddress
# tx_recipt = approve_contract(w3, dataNft_contract_address, 1, info_address_nft_token[1])
# print(f"transaction hash of transfer approve : {(tx_recipt.transactionHash).hex()}")

# # vault_contract_address
# tx_recipt_datanft = transfer_nft_to_datanft_contract(w3, dataNft_contract_address, 1, info_address_nft_token[1], vault_contract_address)
# print(f"transaction hash of transfer datanft to datanft contract : {(tx_recipt_datanft.transactionHash).hex()}")

# if job_result[0]:
#     result = addToWhiteList(w3, job_result[1], vault_contract_address)
#     print(f"result : {result}")
# else:
#     print(False)