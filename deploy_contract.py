import os
from web3 import Web3
from dotenv import load_dotenv
from scripts.deploy_survey_factory import create_nft_datatoken, published_on_ocean
from web3.middleware import geth_poa_middleware


load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv("PROVIDER")))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Check if connected (should return True)
print(w3.isConnected())

# return nft address and token address (datatokenaddress, nftaddress)
info_address_nft_token = create_nft_datatoken(w3)

#published your nft on ocean market
ddo_id = published_on_ocean(w3, info_address_nft_token)

print(f"https://market.oceanprotocol.com/asset/{ddo_id}");