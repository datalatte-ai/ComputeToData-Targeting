import time
import json
import requests

def validate_ddo(ddo):
    ddo_dict = ddo
    data = json.dumps(ddo_dict, separators=(",", ":")).encode("utf-8")
    baseUrl = "https://v4.aquarius.oceanprotocol.com/api/aquarius/assets"
    response = requests.post(
        f"{baseUrl.replace('/v1/', '/')}/ddo/validate",
        data=data,
        headers={"content-type": "application/octet-stream"},
    )

    parsed_response = response.json()

    if parsed_response.get("hash"):
        return True, parsed_response

    return False, parsed_response

def get_ddo(did: str, DDO):
    """Retrieve ddo for a given did."""
    baseUrl = "https://v4.aquarius.oceanprotocol.com/api/aquarius/assets"
    response = requests.get(f"{baseUrl}/ddo/{did}")
    print(response.text)
    if response.status_code == 200:
        response_dict = response.json()
        return DDO

    return None

def wait_for_ddo(did: str, Ddo,timeout=60):
    start = time.time()
    ddo = None
    while not ddo:
        ddo = get_ddo(did=did, DDO=Ddo)
        print(ddo)
        if not ddo:
            time.sleep(0.2)

        if time.time() - start > timeout:
            break

    return ddo