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
from web3.logs import DISCARD
load_dotenv()

oceanProviderUrl = "https://v4.provider.oceanprotocol.com/"
contract_ocean_address = "0xd8992Ed72C445c35Cb4A2be468568Ed1079357c8"
OceanProtocolERC721FactoryAddress = "0x7d46d74023507d30ccc2d3868129fbe4e400e40b"
chain_id = 80001
wallet_address = os.getenv("WALLET_ADDRESS")
private_key = os.getenv("PRIVATE_KEY")
name_of_nft = "dataset(compute)1"
symbol_of_nft = "ts1"
token_uri = "https://ipfs.datalatte.com/ipfs/QmYCK1y5dQnyWeefjnUvpR4oAPQjFEDtUec34UFSYqyKtV"
name_of_datatoken = "dataset(compute)1"
symbol_of_datatoken = "ts1"
name_of_published_assets = "dataset(compute)1"
description_of_published_assets = "testasdasdasdasdasdasdasdasdasdasdasdtest2"
author_of_published_assets = "amqa"
url_donwload_file = "QmcmidkzLUzUggumBieMYHPZE9Cws3hjqYhWQeYE2StHZv"
# url_donwload_file = "https://raw.githubusercontent.com/oceanprotocol/c2d-examples/main/branin_and_gpr/branin.arff"

def create_nft_datatoken_compute(w3):

    # give him address of surveyfactory contract
    address_contract_survey_factory = "0x92A0BE075b2c51c41e93023e4354208bdeeEeF38"
    with open("./contracts/abi/survey_factoryabi.json") as abi_file:
        abi_contract_survey_factory = json.load(abi_file)
    storage_sol_survey_factory = w3.eth.contract(abi=abi_contract_survey_factory, address=address_contract_survey_factory)

    nonce2 = w3.eth.get_transaction_count(wallet_address)
    txn = {
        "chainId": chain_id,
        "from": wallet_address,
        "nonce":w3.eth.get_transaction_count(wallet_address),
        "gasPrice":w3.toWei('40', 'gwei')
    }

    receipt = storage_sol_survey_factory.functions.createNftWithErc20WithFixedRate(
        (
            name_of_nft,
            symbol_of_nft,
            1,
            token_uri,
            True,
            w3.toChecksumAddress(wallet_address.lower()),
        ),
        (
            1,
            [name_of_datatoken,symbol_of_datatoken],
            [
                w3.toChecksumAddress(wallet_address.lower()),
                w3.toChecksumAddress("0x0000000000000000000000000000000000000000".lower()),
                w3.toChecksumAddress("0x0000000000000000000000000000000000000000".lower()),
                w3.toChecksumAddress("0x0000000000000000000000000000000000000000".lower()),
            ],
            [100000000000000000000000,0],
            [],
        ),
        (
            w3.toChecksumAddress(("0x25e1926E3d57eC0651e89C654AB0FA182C6D5CF7").lower()),
            [
                w3.toChecksumAddress(contract_ocean_address.lower()),
                w3.toChecksumAddress(wallet_address.lower()),
                w3.toChecksumAddress(wallet_address.lower()),
                w3.toChecksumAddress("0x0000000000000000000000000000000000000000".lower()),
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
    print(tx_receipt_create_nft)
    rich_logs = storage_sol_survey_factory.events.NFTCreated().processReceipt(tx_receipt_create_nft, errors=DISCARD)
    rich_logs_Token = storage_sol_survey_factory.events.TokenCreated().processReceipt(tx_receipt_create_nft, errors=DISCARD)
    print(rich_logs_Token)
    data_token = rich_logs_Token[0]['args']['newTokenAddress']
    nft_address = rich_logs[0]['args']['newTokenAddress']

    print("nftAddress", nft_address)
    print("dataTokenAddress", data_token)

    return data_token, nft_address


def published_on_ocean_compute(w3, info_address_nft_token):
    assetUrl = {
    "datatokenAddress": info_address_nft_token[0],
    "nftAddress": info_address_nft_token[1],
    "files": [{
            "type": "ipfs",
            "hash": url_donwload_file
        }]
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
        "id": "1",
        "type": "compute",
        "datatokenAddress":info_address_nft_token[0],
        "files": "",
        "serviceEndpoint": "https://v4.provider.oceanprotocol.com",
        "timeout": 86400,
        "compute": {
                "allowRawAlgorithm": False,
                "allowNetworkAccess": True,
                "publisherTrustedAlgorithms": [],
                "publisherTrustedAlgorithmPublishers": [],
            }
    },
    ]
    }


    DDO["id"] = "did:op:" + hashlib.sha256((w3.toChecksumAddress(info_address_nft_token[1]) + str(DDO["chainId"])).encode()).hexdigest()
    encryptedFiles = DataEncryptor.encrypt(objects_to_encrypt=assetUrl, provider_uri= oceanProviderUrl, chain_id=DDO["chainId"])
    DDO["services"][0]["files"] = encryptedFiles.text

    _, proof = validate_ddo(DDO)

    print(proof)
    proof = (
    proof["publicKey"],
    proof["v"],
    proof["r"][0],
    proof["s"][0],
    )

    ddo_string = json.dumps(DDO, separators=(",", ":"))
    metadataHash = hashlib.sha256(ddo_string.encode("utf-8")).hexdigest()
    encryptedDDO = DataEncryptor.encrypt(objects_to_encrypt=ddo_string, provider_uri= oceanProviderUrl, chain_id=DDO["chainId"])

    with open("./contracts/abi/ERC721Abi.json") as f:
        contractERC721TemplateABI = json.load(f)

    # Create nft contract
    nftContract = w3.eth.contract(address=Web3.toChecksumAddress(DDO["nftAddress"]), abi=contractERC721TemplateABI)
    acct = Account.from_key(os.getenv('PRIVATE_KEY'))


    # Build Transaction
    nonce3 = w3.eth.get_transaction_count(acct.address)
    txn_3 = {
    "chainId":chain_id,
    'nonce': nonce3,
    'gas': 900000,
    'gasPrice': w3.toWei('10', 'gwei')
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
    print(f"https://market.oceanprotocol.com/asset/{ddo['id']}");
    return ddo