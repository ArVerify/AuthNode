from flask import Flask, request, jsonify, redirect
from oauthlib.oauth2 import WebApplicationClient
import requests
import json
from arweave_handler import store_on_arweave, tip_received
from config import GOOGLE_DISCOVERY_URL, GOOGLE_CLIENT_SECRET, GOOGLE_CLIENT_ID, FEE

app = Flask(__name__)

if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET and FEE):
    raise Exception("Missing required configuration in .env-File")

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/ping")
def ping():
    return {"status": "alive"}


@app.route("/verify/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    state = json.loads(request.args.get("state").replace("'", "\""))
    address = state["address"]

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return jsonify({'status': 'error', 'message': "User email not available or not verified by Google."}), 400

    print(unique_id, users_email, picture, users_name)

    tx = store_on_arweave(address)

    return redirect("http://127.0.0.1:8080/#/?txId={}".format(tx.id), 200)


@app.route("/verify", methods=['GET'])
def login():
    # get address from query-parameters
    address = request.args.get("address")
    if not address:
        return jsonify({"status": "error", "message": "address is required"}), 400

    # check if a tip has been made by this address
    if tip_received(address, FEE):
        # Find out what URL to hit for Google login
        google_provider_cfg = get_google_provider_cfg()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        # Use library to construct the request for Google login and provide
        # scopes that let you retrieve user's profile from Google
        # add address as state parameter to pass through callback
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=request.base_url + "/callback",
            scope=["openid", "email", "profile"],
            state={"address": address}
        )
        return jsonify({'status': 'success', 'uri': request_uri})

    else:
        return jsonify({"status": "error", "message": "No tip has been received"}), 400


if __name__ == "__main__":
    app.run(debug=True, ssl_context="adhoc")
