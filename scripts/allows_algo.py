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
from ocean_lib.ocean.util import to_wei
from ocean_lib.ocean.ocean import Ocean
# from ocean_lib.web3_internal.utils import connect_to_network
from ocean_lib.example_config import get_config_dict
import os
import time
from decimal import Decimal
from brownie.network import accounts

def allowsAlgorithm(w3, DATA_ddo_dic, ALGO_ddo_dic, ocean):
    bob_pr = os.getenv('PRIVATE_KEY')
    bob = accounts.add(bob_pr)
    # ddo_algo_publish = {
    #     "did":ALGO_ddo['id'],
    #     "containerSectionChecksum":"",
    #     "filesChecksum":ALGO_ddo["files"]
    # }
    # print("================================================================")
    # DATA_ddo['services'][0]['compute']['publisherTrustedAlgorithms'].append({
    #     "did":ALGO_ddo['id'],
    #     "filesChecksum":"",
    #     "containerSectionChecksum":hashlib.sha256(ALGO_ddo["metadata"]["algorithm"]["container"]["entrypoint"] + ALGO_ddo["metadata"]["algorithm"]["container"]["checksum"])
    # })
    # print(DATA_ddo)
    # print("================================================================")
    
    # with open("./contracts/abi/ERC721Abi.json") as f:
    #     contractERC721TemplateABI = json.load(f)

    # # Create nft contract
    # nftContract = w3.eth.contract(address=Web3.toChecksumAddress(DATA_ddo["nftAddress"]), abi=contractERC721TemplateABI)

    # ddo_string = json.dumps(DATA_ddo, separators=(",", ":"))
    # metadataHash = hashlib.sha256(ddo_string.encode("utf-8")).hexdigest()
    # encryptedDDO = DataEncryptor.encrypt(objects_to_encrypt=ddo_string, provider_uri= "https://v4.provider.oceanprotocol.com", chain_id=DATA_ddo["chainId"])
    
    # _, proof = validate_ddo(DATA_ddo)

    # proof = (
    #     proof["publicKey"],
    #     proof["v"],
    #     proof["r"][0],
    #     proof["s"][0],
    # )
    # acct = Account.from_key(os.getenv('PRIVATE_KEY'))

    # nonce3 = w3.eth.get_transaction_count(acct.address)
    # txn_3 = {
    # "chainId":80001,
    # 'nonce': nonce3,
    # 'gas': 900000,
    # 'gasPrice': w3.toWei('10', 'gwei')
    # }
    # wallet_address = os.getenv("WALLET_ADDRESS")
    # setMetaData_function = nftContract.functions.setMetaData(
    #     0,
    #     "https://v4.provider.oceanprotocol.com",
    #     wallet_address.encode('utf-8'),
    #     bytes([2]),
    #     encryptedDDO.text,
    #     metadataHash,
    #     [proof]
    #     ).build_transaction(txn_3)
    # signed_txn = w3.eth.account.sign_transaction(setMetaData_function, os.getenv('PRIVATE_KEY'))

    # # Send the transaction
    # txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    # txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    # print(txn_receipt)

    DATA_ddo = ocean.assets.resolve(DATA_ddo_dic['id'])
    ALGO_ddo = ocean.assets.resolve(ALGO_ddo_dic['id'])
    compute_service = DATA_ddo.services[0]
    compute_service.add_publisher_trusted_algorithm(ALGO_ddo)
    
    dataddo =ocean.assets.update(DATA_ddo, {"from": bob})

    DATA_datatoken = ocean.get_datatoken(DATA_ddo_dic['services'][0]['datatokenAddress'])
    ALGO_datatoken = ocean.get_datatoken(ALGO_ddo_dic['services'][0]['datatokenAddress'])
    
    DATA_datatoken.mint(bob, to_wei(50), {"from": bob})
    ALGO_datatoken.mint(bob, to_wei(50), {"from": bob})
    
    # Convenience variables
    DATA_did = DATA_ddo.did
    ALGO_did = ALGO_ddo.did

    # Operate on updated and indexed assets
    DATA_ddo = ocean.assets.resolve(DATA_did)
    ALGO_ddo = ocean.assets.resolve(ALGO_did)
    compute_service.add_publisher_trusted_algorithm(ALGO_ddo)
    compute_service = DATA_ddo.services[0]
    algo_service = ALGO_ddo.services[0]
    free_c2d_env = ocean.compute.get_free_c2d_environment(compute_service.service_endpoint, DATA_ddo.chain_id)

    from datetime import datetime, timedelta, timezone
    from ocean_lib.models.compute_input import ComputeInput

    DATA_compute_input = ComputeInput(DATA_ddo, compute_service)
    ALGO_compute_input = ComputeInput(ALGO_ddo, algo_service)

    print(free_c2d_env["consumerAddress"])
    print(free_c2d_env["id"])
    dat = [DATA_compute_input]
    print(dat[0].service.service_endpoint)
    # Pay for dataset and algo for 1 day
    datasets, algorithm = ocean.assets.pay_for_compute_service(
        datasets=[DATA_compute_input],
        algorithm_data=ALGO_compute_input,
        consume_market_order_fee_address=bob.address,
        tx_dict={"from": bob},
        compute_environment=free_c2d_env["id"],
        valid_until=int((datetime.now(timezone.utc) + timedelta(days=1)).timestamp()),
        consumer_address=free_c2d_env["consumerAddress"],
    )
    # assert datasets, "pay for dataset unsuccessful"
    # assert algorithm, "pay for algorithm unsuccessful"
    print("----------------------------------------------------------")
    # Start compute job
    job_id = ocean.compute.start(
        consumer_wallet=bob,
        dataset=datasets[0],
        compute_environment=free_c2d_env["id"],
        algorithm=algorithm,
    )
    print(f"Started compute job with id: {job_id}")
    succeeded = False
    for _ in range(0, 200):
        status = ocean.compute.status(DATA_ddo, compute_service, job_id, bob)
        if status.get("dateFinished") and Decimal(status["dateFinished"]) > 0:
            succeeded = True
            break
    time.sleep(5)
    print(succeeded)
    output = ocean.compute.compute_job_result_logs(
    DATA_ddo, compute_service, job_id, bob, 'output'
    )[0]
    return output, bob.address