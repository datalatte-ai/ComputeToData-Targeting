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

oceanProviderUrl = "https://v4.provider.mumbai.oceanprotocol.com"
contract_ocean_address = "0xd8992Ed72C445c35Cb4A2be468568Ed1079357c8"
OceanProtocolERC721FactoryAddress = "0x7d46d74023507d30ccc2d3868129fbe4e400e40b"
chain_id = 80001
wallet_address = os.getenv("WALLET_ADDRESS")
private_key = os.getenv("PRIVATE_KEY")
name_of_nft = "algo_test"
symbol_of_nft = "al2"
token_uri = "https://ipfs.datalatte.com/ipfs/QmYCK1y5dQnyWeefjnUvpR4oAPQjFEDtUec34UFSYqyKtV"
name_of_datatoken = "algo_test_2"
symbol_of_datatoken = "alg2"
name_of_published_assets = "algo"
description_of_published_assets = "algo alog algo"
author_of_published_assets = "algo"
url_donwload_file = "QmcmidkzLUzUggumBieMYHPZE9Cws3hjqYhWQeYE2StHZv"

def create_nft_datatoken(w3):

    # give him address of surveyfactory contract
    address_contract_survey_factory = "0x42390ac80f1b2CA28F2d38E62D57dd1D534bE7fa"
    with open("./contracts/abi/survey_factoryabi.json") as abi_file:
        abi_contract_survey_factory = json.load(abi_file)
    # abi_contract_survey_factory = '[{"inputs":[{"internalType":"address","name":"oceanFactoryAddress","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"newTokenAddress","type":"address"},{"indexed":true,"internalType":"address","name":"templateAddress","type":"address"},{"indexed":false,"internalType":"string","name":"tokenName","type":"string"},{"indexed":true,"internalType":"address","name":"admin","type":"address"},{"indexed":false,"internalType":"string","name":"symbol","type":"string"},{"indexed":false,"internalType":"string","name":"tokenURI","type":"string"},{"indexed":false,"internalType":"bool","name":"transferable","type":"bool"},{"indexed":true,"internalType":"address","name":"creator","type":"address"}],"name":"NFTCreated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"newTokenAddress","type":"address"},{"indexed":true,"internalType":"address","name":"templateAddress","type":"address"},{"indexed":false,"internalType":"string","name":"name","type":"string"},{"indexed":false,"internalType":"string","name":"symbol","type":"string"},{"indexed":false,"internalType":"uint256","name":"cap","type":"uint256"},{"indexed":false,"internalType":"address","name":"creator","type":"address"}],"name":"TokenCreated","type":"event"},{"inputs":[{"components":[{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"symbol","type":"string"},{"internalType":"uint256","name":"templateIndex","type":"uint256"},{"internalType":"string","name":"tokenURI","type":"string"},{"internalType":"bool","name":"transferable","type":"bool"},{"internalType":"address","name":"owner","type":"address"}],"internalType":"struct OPFactory.NftCreateData","name":"nftData","type":"tuple"},{"components":[{"internalType":"uint256","name":"templateIndex","type":"uint256"},{"internalType":"string[]","name":"strings","type":"string[]"},{"internalType":"address[]","name":"addresses","type":"address[]"},{"internalType":"uint256[]","name":"uints","type":"uint256[]"},{"internalType":"bytes[]","name":"bytess","type":"bytes[]"}],"internalType":"struct OPFactory.ErcCreateData","name":"ercData","type":"tuple"},{"components":[{"internalType":"address","name":"fixedPriceAddress","type":"address"},{"internalType":"address[]","name":"addresses","type":"address[]"},{"internalType":"uint256[]","name":"uints","type":"uint256[]"}],"internalType":"struct OPFactory.FixedData","name":"fixedData","type":"tuple"}],"name":"createNftWithErc20WithFixedRate","outputs":[],"stateMutability":"nonpayable","type":"function"}]'
    storage_sol_survey_factory = w3.eth.contract(abi=abi_contract_survey_factory, address=address_contract_survey_factory)

    nonce2 = w3.eth.get_transaction_count(wallet_address)
    txn = {
        "chainId": chain_id,
        "from": wallet_address,
        "nonce": nonce2,
        'gas': 1600000,  # Adjust as needed
        'gasPrice': w3.toWei('2.5', 'gwei')
    }

    receipt = storage_sol_survey_factory.functions.createNftWithErc20(
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
        )
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

    data_token = rich_logs_Token[0]['args']['newTokenAddress']
    nft_address = rich_logs[0]['args']['newTokenAddress']

    print("nftAddress", nft_address)
    print("dataTokenAddress", data_token)

    return data_token, nft_address


def published_on_ocean(w3, info_address_nft_token):
    assetUrl = {
    "datatokenAddress": info_address_nft_token[0],
    "nftAddress": info_address_nft_token[1],
    "files": [{
            "type": "ipfs",
            "hash": url_donwload_file
        }]
    }

    date_created = datetime.now().isoformat()
    image = "oceanprotocol/algo_dockers"
    tag = "python-branin"
    checksum = "sha256:8221d20c1c16491d7d56b9657ea09082c0ee4a8ab1a6621fa720da58b09580e4"
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
    "type": "algorithm",
    "name": name_of_published_assets,
    "description": description_of_published_assets,
    "author": author_of_published_assets,
    "license": "MIT",
    "algorithm":{
                "language": "python",
                "format": "docker-image",
                "version": "0.1",
                "container": {
                    "entrypoint": "python $ALGO",
                    "image": image,
                    "tag": tag,
                    "checksum": checksum,
                },
            }
    },
    "services": [
    {
        "id": "1",
        "type": "compute",
        "files": "",
        "datatokenAddress": info_address_nft_token[0],
        "serviceEndpoint": "https://v4.provider.mumbai.oceanprotocol.com",
        "timeout": 0,
        "compute_values":{
            "allowRawAlgorithm": False,
            "allowNetworkAccess": True,
            "publisherTrustedAlgorithms": [],
            "publisherTrustedAlgorithmPublishers": [],
        }
    },
    ],
    }


    DDO["id"] = "did:op:" + hashlib.sha256((w3.toChecksumAddress(info_address_nft_token[1]) + str(DDO["chainId"])).encode()).hexdigest()
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

    return ddo['id']