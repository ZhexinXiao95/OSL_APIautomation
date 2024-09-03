import asyncio

from utils.log import logger
from utils.request_connect import v3_mk_request
from utils.ws_connect import WebSocketClient, websocket_connection


def get_ws_token():
    res = v3_mk_request("POST", "api/3/bcg/rest/auth/token")
    return res['res']['token']


def establish_connection(ws_msg):
    auth_token = get_ws_token()
    asyncio.run(websocket_connection(ws_msg, auth_token))

if __name__ == '__main__':
    token = get_ws_token()
    msg = {
        "messageType": "subscribe",
        "instrument": "BTC.USD",
        "tag": "For future use",
        "quantity": 0.0001,
        "currency": "BTC",
        "accountGrpUuid": ""
    }
    establish_connection(msg)
