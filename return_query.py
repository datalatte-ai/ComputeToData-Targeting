import json
import os
def get_input(local=False):
    if local:
        print("Reading local file branin.arff.")

        return "branin.arff"

    dids = os.getenv("DIDS", None)

    if not dids:
        print("No DIDs found in environment. Aborting.")
        return

    dids = json.loads(dids)

    for did in dids:
        filename = f"data/inputs/{did}/0"  # 0 for metadata service
        print(f"Reading asset file {filename}.")

        return filename
    

def run(local=False):
    filename = get_input(local)
    if not filename:
        print("Could not retrieve filename.")
        return

    with open(filename) as datafile:
        result = json.load(datafile)


    if result['gender'] == 'male' and result['age'] == "25-34":
        print("YES")