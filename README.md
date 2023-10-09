# ComputeToData-Targeting

## Deployment Instructions

This document provides instructions on how to deploy the C2D contract using Python 3.10.11 on Ocean.

### Prerequisites

Ensure that Python 3.10.11 is installed on your system.

### Installation

1. Open the command prompt or terminal.
2. Navigate to the project directory.
3. Install the necessary dependencies by executing the following command:

```shell
pip install ocean-lib
```
## Deployment
1. Ensure that you are in the project directory.
2. Insert your custom wallet address into the 'white_list_wallet_addresses_cid' variable, which is located in the 'deploy_survey_vault.py' file within the scripts directory.
3. Run the application by executing the following command:

```shell
python deploy_contract.py
```
