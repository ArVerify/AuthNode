import arweave
from simple_graphql_client import GraphQLClient, load
from config import ARWEAVE_KEYFILE
from typing import Union

wallet = arweave.Wallet(ARWEAVE_KEYFILE)

gql_client = GraphQLClient(base_url="https://arweave.dev/graphql")


def tip_received(owner: str, fee: float) -> bool:
    recipient = wallet.address
    query = load("queries/tipped.gql")
    variables = {
        "owner": owner,
        "recipient": recipient
    }
    response = gql_client.query(query, variables)
    edges = response['data']['transactions']['edges']
    if not edges:
        return False
    node = edges[0]['node']
    quantity = float(node['quantity']['ar'])
    return quantity == fee


def get_verification_id(verified_address: str, auth_nodes: [str]) -> Union[str, None]:
    query = load("queries/verified.gql")
    variables = {
        "address": verified_address,
        "authNodes": auth_nodes
    }
    response = gql_client.query(query, variables)
    edges = response['data']['transactions']['edges']
    if not edges:
        return None
    else:
        return edges[0]['node']['id']


def store_on_arweave(verified_address: str) -> str:
    auth_nodes = ["s-hGrOFm1YysWGC3wXkNaFVpyrjdinVpRKiVnhbo2so"]
    transaction_id = get_verification_id(verified_address, auth_nodes)
    if not transaction_id:
        # store verification on chain
        transaction = arweave.Transaction(wallet)
        transaction.add_tag(name="App-Name", value="ArVerifyDev")
        transaction.add_tag(name="Type", value="Verification")
        transaction.add_tag(name="Method", value="Google")
        transaction.add_tag(name="Address", value=verified_address)
        transaction.sign()
        _fee = transaction.get_price()
        transaction.send()

        return transaction.id
    else:
        return transaction_id
