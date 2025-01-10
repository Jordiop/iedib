import urllib.request
import json
import os
import ssl

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

# Request data goes here
# The example below assumes JSON formatting which may be updated
# depending on the format your endpoint expects.
# More information can be found here:
# https://docs.microsoft.com/azure/machine-learning/how-to-deploy-advanced-entry-script
data = {
    "Inputs": {
        "data": [{
            'island': 'Biscoe',
            'culmen_length_mm': 50.0,
            'culmen_depth_mm': 15.0,
            'flipper_length_mm': 220,
            'body_mass_g': 5000,
            'sex': 'Male'
        },
        {
            'island': 'Dream',
            'culmen_length_mm': 35.0,
            'culmen_depth_mm': 17.0,
            'flipper_length_mm': 185,
            'body_mass_g': 3400,
            'sex': 'Female'
        }]
    },
}
        

body = str.encode(json.dumps(data))

url = 'http://a1a2cba1-a1ce-4c2c-b3c7-75b18f73de0b.westeurope.azurecontainer.io/score'
# Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
api_key = 'ZMbadJ6uHzZSAhkLOrvl6owL1BauosJ7'
if not api_key:
    raise Exception("A key should be provided to invoke the endpoint")


headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

req = urllib.request.Request(url, body, headers)

try:
    response = urllib.request.urlopen(req)

    result = response.read()
    print(result)
except urllib.error.HTTPError as error:
    print("The request failed with status code: " + str(error.code))

    # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
    print(error.info())
    print(error.read().decode("utf8", 'ignore'))
