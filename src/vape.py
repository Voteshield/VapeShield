from hypothesis import settings, Phase
import json
import requests
from requests.auth import HTTPBasicAuth
from time import sleep
import urllib.request
import schemathesis
import os

DEFAULT_TIMEOUT = 10
environment = os.environ.get('ENVIRONMENT_ARG')
base_url = os.environ.get('BASE_URL_ARG')
retry_attempts = int(os.environ.get('RETRY_ATTEMPTS', 60))
retry_timeout = int(os.environ.get('RETRY_TIMEOUT', 2))

if os.path.exists('apikeys.json'):
    with open('apikeys.json') as json_file:
        keysdict = json.load(json_file)
else:
    keysdict = json.loads(os.environ.get('VS_API_KEY'))

# Most of the time, if this is being ran it is after a new environment is created, 
# and there may be a window when services are being cycled. So we wait for 200s.
for i in range(retry_attempts):
    health_url = "{}/_health/".format(base_url)
    try:
        r = requests.get(health_url)
        if r.status_code == 200:
            break
    except Exception as err:
        print("Attempt {0}/{1} error: {2}".format(i + 1, retry_attempts, err))
    if i is not retry_attempts - 1:
        sleep(retry_timeout)

# This is required because of this:
# https://github.com/flasgger/flasgger/issues/267
jsonurl = urllib.request.urlopen("{}/v1/spec.json".format(base_url))
schema_dict = json.loads(jsonurl.read())
schema_dict.pop('definitions', None)
schema = schemathesis.from_dict(
    schema_dict, 
    base_url=base_url, 
    skip_deprecated_operations=True,
)

# Get our access token by exchanging our keys for it.
def bearer_access_token():
    query = {
        "grant_type": "refresh_token",
        "client_id": keysdict['ClientId'],
        "refresh_token": keysdict['refresh_token'],
        "scope": "CognitoGroup/Developers",
    }
    r = requests.post(
        "https://oauth.{}.us/oauth2/token".format(environment),
        data=query,
        auth=HTTPBasicAuth(keysdict['ClientId'], keysdict['ClientSecret']),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response = r.json()
    return response['access_token']

print(bearer_access_token())

# For now, population and tag routes are excluded.
#@schema.parametrize(endpoint="^/(?!populations|tags)",)
@schema.parametrize(method="GET")
@settings(phases=[Phase.explicit], deadline=None)
def test_api(case):
    # Slow routes are defined here. Don't really know of a way to not hard code these.
    timeout = {
        ("GET", "/changes"): 120,
        ("GET", "/change_history"): 60,
        ("GET", "/compare"): 60,
        ("GET", "/download_population"): 120,
        ("GET", "/notable_populations"): 60,
        ("GET", "/system/snapshots"): 60
    }.get((case.operation.method.upper(), case.operation.path), DEFAULT_TIMEOUT)
    case.headers = case.headers or {}
    case.headers["Authorization"] = "Bearer " + f"{bearer_access_token()}"
    case.call_and_validate(timeout=timeout)