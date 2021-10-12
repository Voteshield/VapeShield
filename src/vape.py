from hypothesis import settings, Phase
import json
import requests
from requests.auth import HTTPBasicAuth
import urllib.request
import schemathesis
import os

DEFAULT_TIMEOUT = 10
environment = os.environ.get('ENVIRONMENT', '***REMOVED***')
base_url = os.environ.get('BASE_URL', 'https://api-vs.***REMOVED***.us')

if os.path.exists('apikeys.json'):
    with open('apikeys.json') as json_file:
        keysdict = json.load(json_file)
else:
    keysdict = os.environ.get('VS_API_KEY')
    if not keysdict:
        raise SystemExit('No API keyfile found.')

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


# For now, population and tag routes are excluded.
#@schema.parametrize(endpoint="^/(?!populations|tags)",)
@schema.parametrize(method="GET")
@settings(phases=[Phase.explicit], deadline=None)
def test_api(case):
    # Slow routes are defined here. Don't really know of a way to not hard code these.
    timeout = {
        ("GET", "/changes"): 60,
        ("GET", "/change_history"): 60,
        ("GET", "/download_population"): 60,
        ("GET", "/system/snapshots"): 60
    }.get((case.operation.method.upper(), case.operation.path), DEFAULT_TIMEOUT)
    case.headers = case.headers or {}
    case.headers["Authorization"] = "Bearer " + f"{bearer_access_token()}"
    case.call_and_validate(timeout=timeout)