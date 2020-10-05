# ArVerify - AuthNode
ArVerify is service which allows users to have their addresses verified via Google Sign On.
The verification process is implemented inside an AuthNode.
To ensure that every AuthNode can be trusted, the AuthNode is
staked in the DAO. 

## Setup
### Prerequisites
1.  Create a `.env`-File with the following structure:
    ```
    FEE=(you choose the Fee, its in AR)
    GOOGLE_CLIENT_ID=...
    GOOGLE_CLIENT_SECRET=...
    DOMAIN=...
    ```
2.  Copy your arweave-keyfile into the directory and save
    it as `arweave-keyfile.json`
### Run the server
The server is will run on port 8000.
#### Dockerfile
A public Dockerfile will be released soon
1. `docker build --tag arverfify:authnode .`
2. `docker run --publish 8000:8000 --detach --name arverify-authnode arverfify:authnode`
#### Manual setup
1. `pip install -r requirements.txt gunicorn==20.0.4`
2. `gunicorn -b 0.0.0.0 -w 4 auth_node:app`

## Routes
*   GET /ping

    Returns `{"status": "alive"}` when the AuthNode is healthy
    
*   GET /verify?address={ADDRESS_TO_BE_VERIFIED}

    Returns  `{'status': 'success', 'uri': [request_uri]}` when the user successfully tipped the node. The URI
    is the sing-in URI for the Google Log-In

*   GET /verify/callback

    Returns `{'status': 'success', 'id': [TX_ID]}` when verification was successful
    
