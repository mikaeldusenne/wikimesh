import requests
from os.path import split
import logging

s = requests.Session()

search = "asthma"

def get_descriptor(search):
    url = "https://id.nlm.nih.gov/mesh/lookup/descriptor"
    args = {
        "label": search,
        "match": "exact",
        "limit": 10
    }
    resp = s.get(url, params=args)
    assert resp.status_code == 200
    j = resp.json()
    try:
        return split(j[0]['resource'])[-1]
    except Exception:
        logging.warning(f'no descriptor found for {search}, response: {j}')


# descriptor = get_descriptor("asthma")

# url = "https://id.nlm.nih.gov/mesh/lookup/pair" # qualifiers
# args = {"descriptor": descriptor}

# resp = s.get(url, params=args)
# resp.json()

# descriptor
