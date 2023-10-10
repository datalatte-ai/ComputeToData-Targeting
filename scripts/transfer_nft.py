import os
import json
from web3 import Web3
from web3 import Account
from dotenv import load_dotenv

load_dotenv()
chain_id = 80001
wallet_address = os.getenv("WALLET_ADDRESS")
private_key = os.getenv("PRIVATE_KEY")

def transfer_nft_to_datanft_contract(w3, dataNft_contract_address, token_id, nft_address, survey_vault_contract_address):
    with open("./contracts/abi/dataNft_abi.json") as f:
        contract_dataNft_abi = json.load(f)

    # Create nft contract
    nftContract = w3.eth.contract(address=dataNft_contract_address, abi=contract_dataNft_abi)
    acct = Account.from_key(os.getenv('PRIVATE_KEY'))


    # Build Transaction
    nonce3 = w3.eth.get_transaction_count(acct.address)
    txn_3 = {
    "chainId":chain_id,
    'nonce': nonce3,
    'gas': 900000,
    'gasPrice': w3.to_wei('10', 'gwei')
    }


    # Building a transaction to call the `setMetaData` function of the contract
    setMetaData_function = nftContract.functions.TransferNft(
    nft_address,
    wallet_address,
    token_id,
    survey_vault_contract_address
    ).build_transaction(txn_3)


    # Sign the transaction
    signed_txn = w3.eth.account.sign_transaction(setMetaData_function, private_key)

    # Send the transaction
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

    return txn_receipt