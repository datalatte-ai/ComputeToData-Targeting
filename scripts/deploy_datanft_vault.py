import os
import json
from dotenv import load_dotenv
from solcx import compile_standard, install_solc

load_dotenv()

contract_token_address = "0xd8992Ed72C445c35Cb4A2be468568Ed1079357c8"
amount_token_to_give_by_per_cid= 10
white_list_wallet_addresses_cid = ["wallet_1","wallet_2",...,"wallet_n"]
chain_id = 80001
wallet_address = os.getenv("WALLET_ADDRESS")
private_key = os.getenv("PRIVATE_KEY")


def dataNft_vault(w3):
    with open("./contracts/DatanftVault.sol", "r") as file:
        simple_storage_file = file.read()

    install_solc("0.8.19")
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"DatanftVault.sol": {"content": simple_storage_file}},
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

    with open("survey_vault.json", "w") as file:
        json.dump(compiled_sol, file)
    contract_bytecode = compiled_sol["contracts"]["DatanftVault.sol"]["DataNftVault"]["evm"]["bytecode"]["object"]
    contract_abi = json.loads(compiled_sol["contracts"]["DatanftVault.sol"]["DataNftVault"]["metadata"])["output"]["abi"]

    with open('./contracts/abi/dataNft_abi.json', 'w') as outfile:
        json.dump(contract_abi, outfile)

    contract = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
    nonce = w3.eth.get_transaction_count(wallet_address)

    transaction = contract.constructor().build_transaction(
        {"chainId": chain_id, "from": wallet_address, "nonce": nonce}
    )
    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"deploy dataNft contract with this address : {tx_receipt.contractAddress}")

    return tx_receipt.contractAddress