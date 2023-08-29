from ocean_lib.ocean.ocean import Ocean
from ocean_lib.web3_internal.utils import connect_to_network
from ocean_lib.example_config import get_config_dict
import os
from brownie.network import accounts

def allowsAlgorithm(DATA_ddo, ALGO_ddo):
    bob_pr = os.getenv('PRIVATE_KEY')
    bob = accounts.add(bob_pr)
    config = get_config_dict("polygon-test")
    ocean = Ocean(config)
    compute_service = DATA_ddo.services[1]
    compute_service.add_publisher_trusted_algorithm(ALGO_ddo)
    
    # Convenience variables
    DATA_did = DATA_ddo.did
    ALGO_did = ALGO_ddo.did

    # Operate on updated and indexed assets
    DATA_ddo = ocean.assets.resolve(DATA_did)
    ALGO_ddo = ocean.assets.resolve(ALGO_did)

    compute_service = DATA_ddo.services[1]
    algo_service = ALGO_ddo.services[0]
    free_c2d_env = ocean.compute.get_free_c2d_environment(compute_service.service_endpoint, DATA_ddo.chain_id)

    from datetime import datetime, timedelta, timezone
    from ocean_lib.models.compute_input import ComputeInput

    DATA_compute_input = ComputeInput(DATA_ddo, compute_service)
    ALGO_compute_input = ComputeInput(ALGO_ddo, algo_service)

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
    assert datasets, "pay for dataset unsuccessful"
    assert algorithm, "pay for algorithm unsuccessful"

    # Start compute job
    job_id = ocean.compute.start(
        consumer_wallet=bob,
        dataset=datasets[0],
        compute_environment=free_c2d_env["id"],
        algorithm=algorithm,
    )
    print(f"Started compute job with id: {job_id}")
    return job_id