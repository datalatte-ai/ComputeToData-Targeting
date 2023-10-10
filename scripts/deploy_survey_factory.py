import os
import json
import hashlib
from web3 import Web3
from web3 import Account
from datetime import datetime
from dotenv import load_dotenv
from helpers.helper import validate_ddo, wait_for_ddo
from solcx import compile_standard, install_solc
from ocean_lib.data_provider.data_encryptor import DataEncryptor

load_dotenv()

oceanProviderUrl = "https://v4.provider.mumbai.oceanprotocol.com"
contract_ocean_address = "0xd8992Ed72C445c35Cb4A2be468568Ed1079357c8"
OceanProtocolERC721FactoryAddress = "0x7d46d74023507d30ccc2d3868129fbe4e400e40b"
chain_id = 80001
wallet_address = os.getenv("WALLET_ADDRESS")
private_key = os.getenv("PRIVATE_KEY")
name_of_nft = "test"
symbol_of_nft = "ts1"
token_uri = "url"
name_of_datatoken = "test"
symbol_of_datatoken = "tes1"
contract_address_survey_factory = "0x32809f8E41a9EF5b08c11654b9d4b18B5CeD172c"
name_of_published_assets = "test"
description_of_published_assets = "test"
author_of_published_assets = "test"

def survey_factory(w3):
    with open("./contracts/SurveyFactory.sol", "r") as file:
        simple_storage_file = file.read()

    install_solc("0.8.19")
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"SurveyFactory.sol": {"content": simple_storage_file}},
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                    }
                }
            },
        },
        solc_version="0.8.19",
    )

    with open("survey_factory.json", "w") as file:
        json.dump(compiled_sol, file)
    contract_bytecode = compiled_sol["contracts"]["SurveyFactory.sol"]["SurveyFactory"]["evm"]["bytecode"]["object"]
    contract_abi = json.loads(compiled_sol["contracts"]["SurveyFactory.sol"]["SurveyFactory"]["metadata"])["output"]["abi"]

    contract = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
    nonce = w3.eth.get_transaction_count(wallet_address)

    transaction = contract.constructor(w3.to_checksum_address(OceanProtocolERC721FactoryAddress)).build_transaction(
        {"chainId": chain_id, "from": w3.to_checksum_address(wallet_address), "nonce": nonce}
    )
    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"deploy surveyfactory contract with this address : {tx_receipt.contractAddress}")

    return contract_abi, tx_receipt.contractAddress



def create_nft_datatoken(w3):

    info_contract_survey_factory = survey_factory(w3)

    storage_sol_survey_factory = w3.eth.contract(abi=info_contract_survey_factory[0], address=info_contract_survey_factory[1])

    nonce2 = w3.eth.get_transaction_count(wallet_address)
    txn = {
        "chainId": chain_id,
        "from": wallet_address,
        "nonce": nonce2,
        'gas': 1600000,  # Adjust as needed
        'gasPrice': w3.to_wei('2.5', 'gwei')
    }

    receipt = storage_sol_survey_factory.functions.createNftWithErc20WithFixedRate(
        (
            name_of_nft,
            symbol_of_nft,
            1,
            token_uri,
            True,
            w3.to_checksum_address(wallet_address.lower()),
        ),
        (
            1,
            [name_of_datatoken,symbol_of_datatoken],
            [
                w3.to_checksum_address(wallet_address.lower()),
                w3.to_checksum_address("0x0000000000000000000000000000000000000000".lower()),
                w3.to_checksum_address("0x0000000000000000000000000000000000000000".lower()),
                w3.to_checksum_address("0x0000000000000000000000000000000000000000".lower()),
            ],
            [100000000000000000000000,0],
            [],
        ),
        (
            w3.to_checksum_address(("0x25e1926E3d57eC0651e89C654AB0FA182C6D5CF7").lower()),
            [
                w3.to_checksum_address(contract_ocean_address.lower()),
                w3.to_checksum_address(wallet_address.lower()),
                w3.to_checksum_address(wallet_address.lower()),
                w3.to_checksum_address("0x0000000000000000000000000000000000000000".lower()),
            ],
            [
            18,18,1000000000000000000,1000000000000000,1
            ],
        ),
    ).build_transaction(txn)

    # Sign the transaction
    signed_txn = w3.eth.account.sign_transaction(receipt, private_key)
    # Send the transaction
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    tx_receipt_create_nft = w3.eth.get_transaction_receipt(txn_hash.hex())
    # replace 'transaction_hash' with actual value
    rich_logs = storage_sol_survey_factory.events.NFTCreated().process_receipt(tx_receipt_create_nft)
    rich_logs_Token = storage_sol_survey_factory.events.TokenCreated().process_receipt(tx_receipt_create_nft)

    data_token = rich_logs_Token[0]['args']['newTokenAddress']
    nft_address = rich_logs[0]['args']['newTokenAddress']

    print("nftAddress", nft_address)
    print("dataTokenAddress", data_token)

    return data_token, nft_address


def published_on_ocean(w3, info_address_nft_token, vault_contract_address):
    assetUrl = {
    "datatokenAddress": info_address_nft_token[0],
    "nftAddress": info_address_nft_token[1],
    "files": [
        {
            "type": "smartcontract",
            "chainId": chain_id,
            "address": vault_contract_address,
            "abi": {
                "inputs": [],
                "name": "getValidCids",
                "outputs": [
                    {
                        "internalType": "string[]",
                        "name": "",
                        "type": "string[]"
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            }
        }
    ]
    }

    date_created = datetime.now().isoformat()
    # Prepare DDO
    DDO = {
    "@context": ["https://w3id.org/did/v1"],
    "id": "",
    "version": "4.1.0",
    "chainId": chain_id,
    "nftAddress": info_address_nft_token[1],
    "metadata": {
    "created": date_created,
    "updated": date_created,
    "type": "dataset",
    "name": name_of_published_assets,
    "description": description_of_published_assets,
    "author": author_of_published_assets,
    "license": "MIT",
    },
    "services": [
    {
        "id": "access-contract-service",
        "type": "access",
        "files": "",
        "datatokenAddress": info_address_nft_token[0],
        "serviceEndpoint": "https://v4.provider.mumbai.oceanprotocol.com",
        "timeout": 0,
    },
    ],
    }


    DDO["id"] = "did:op:" + hashlib.sha256((w3.to_checksum_address(info_address_nft_token[1]) + str(DDO["chainId"])).encode()).hexdigest()
    encryptedFiles = DataEncryptor.encrypt(objects_to_encrypt=assetUrl, provider_uri= oceanProviderUrl, chain_id=DDO["chainId"])
    DDO["services"][0]["files"] = encryptedFiles.text

    _, proof = validate_ddo(DDO)

    proof = (
    proof["publicKey"],
    proof["v"],
    proof["r"][0],
    proof["s"][0],
    )

    ddo_string = json.dumps(DDO, separators=(",", ":"))
    metadataHash = hashlib.sha256(ddo_string.encode("utf-8")).hexdigest()
    encryptedDDO = DataEncryptor.encrypt(objects_to_encrypt=ddo_string.encode("utf-8"), provider_uri= oceanProviderUrl, chain_id=DDO["chainId"])

    with open("./contracts/abi/ERC721Abi.json") as f:
        contractERC721TemplateABI = json.load(f)

    # Create nft contract
    nftContract = w3.eth.contract(address=Web3.to_checksum_address(DDO["nftAddress"]), abi=contractERC721TemplateABI)
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
    setMetaData_function = nftContract.functions.setMetaData(
    0,
    oceanProviderUrl,
    wallet_address.encode('utf-8'),
    bytes([2]),
    encryptedDDO.text,
    metadataHash,
    [proof]
    ).build_transaction(txn_3)


    # Sign the transaction
    signed_txn = w3.eth.account.sign_transaction(setMetaData_function, private_key)

    # Send the transaction
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

    ddo = wait_for_ddo(did=DDO["id"], Ddo=DDO)

    return ddo['id']