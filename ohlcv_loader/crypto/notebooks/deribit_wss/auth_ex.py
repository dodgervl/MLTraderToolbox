# built ins
import sys
import time
from datetime import datetime, timedelta
import hashlib
import hmac
import json
import secrets

# installed
import websocket

# imported from project
from deribit import DeribitAPIAccessScope, DeribitExchangeVersion

sys.path.append(
    '/home/elliotp/dev/deribit/API-Guide/deribit_examples/User-Credentials')  # noqa: E501
from user import Client_Id, Client_Secret  # noqa: E402 E501


class UserWebsocketEngine:
    def __init__(self, client_Id, scope, exchange_version):
        self.client_id = client_Id
        self.scope = scope
        self.exchange_version = exchange_version
        self.expiry_time = None
        self.seconds_delay = 10
        self.refresh_token = ''
        self.authentication_refresh_flag = 0
        self.heartbeat_requested_flag = 0
        self.heartbeat_set_flag = 0
        self.main()

    def main(self):
        def on_message(ws, message):
            message = json.loads(message)
            print("Message Received at: " + str(datetime.now().time().strftime('%H:%M:%S')))  # noqa: E501
            # print(message)

            if 'error' in message.keys():
                error_message = message['error']['message']
                error_code = message['error']['code']
                print('You have received an ERROR MESSAGE: {} with the ERROR CODE: {}'.format(error_message,
                                                                                              error_code))  # noqa: E501

            # display successful authentication messages as well as stores your refresh_token                                 # noqa: E501
            if 'result' in message.keys():
                if type(message['result']) == list:
                    for a in range(0, len(message['result'])):
                        if all(column_name in message['result'][a].keys() for column_name in
                               ['total_profit_loss', 'size_currency', 'size', 'settlement_price',  # noqa: E501
                                'realized_profit_loss', 'realized_funding', 'open_orders_margin',  # noqa: E501
                                'mark_price', 'maintenance_margin', 'leverage', 'kind', 'instrument_name',  # noqa: E501
                                'initial_margin', 'index_price', 'floating_profit_loss',  # noqa: E501
                                'estimated_liquidation_price', 'direction', 'delta', 'average_price']):  # noqa: E501
                            print('Present Positions at: ' + str(
                                datetime.now().time().strftime('%H:%M:%S')))  # noqa: E501
                            print(message)
                if [*message['result']] == ['token_type', 'scope', 'refresh_token', 'expires_in',
                                            'access_token']:  # noqa: E501
                    if self.authentication_refresh_flag == 1:
                        print('Successfully Refreshed your Authentication at: ' +
                              str(datetime.now().time().strftime('%H:%M:%S')))
                    else:
                        print('Authentication Success at: ' + str(
                            datetime.now().time().strftime('%H:%M:%S')))  # noqa: E501
                    self.refresh_token = message['result']['refresh_token']
                    if message['testnet']:
                        # The testnet returns an extremely high value for expires_in and is best to use                       # noqa: E501
                        # 600 in place as so the functionality is as similar as the Live exchange                             # noqa: E501
                        expires_in = 600
                    else:
                        expires_in = message['result']['expires_in']

                    self.expiry_time = (datetime.now() + timedelta(seconds=expires_in))  # noqa: E501
                    print('Authentication Expires at: ' + str(self.expiry_time.strftime('%H:%M:%S')))  # noqa: E501

            # uses your refresh_token to refresh your authentication
            if datetime.now() > self.expiry_time and self.authentication_refresh_flag == 0:  # noqa: E501
                self.authentication_refresh_flag = 1
                print('Refreshing your Authentication at: ' + str(self.expiry_time.strftime('%H:%M:%S')))  # noqa: E501
                ws_data = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "public/auth",
                    "params": {
                        "grant_type": "refresh_token",
                        "refresh_token": self.refresh_token
                    }
                }
                ws.send(json.dumps(ws_data))

            # heartbeat set success check and heartbeat response
            if 'params' in message.keys():
                if message['params']['type'] == 'heartbeat' and self.heartbeat_set_flag == 0:  # noqa: E501
                    self.heartbeat_set_flag = 1
                    print('Heartbeat Successfully Initiated at: ' + str(
                        datetime.now().time().strftime('%H:%M:%S')))  # noqa: E501

                if message['params']['type'] == 'test_request':
                    ws_data = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "public/test",
                        "params": {
                        }
                    }
                    ws.send(json.dumps(ws_data))
            # get_positions API request
            ws_data = {"jsonrpc": "2.0", "id": 1,
                       "method": "private/get_positions",
                       "params": {
                           "currency": "BTC",
                           "kind": "future"}}
            ws.send(json.dumps(ws_data))

            # natural delay
            print('Pending {} Second Introduced Delay at: '.format(self.seconds_delay) + str(
                datetime.now().time().strftime('%H:%M:%S')))  # noqa: E501
            time.sleep(self.seconds_delay)

        def on_error(ws, error):
            if type(error == "<class 'websocket._exceptions.WebSocketBadStatusException'>"):  # noqa: E501
                print('')
                print(
                    'ERROR MESSAGE:' + 'Testnet is likely down for maintenance or your connection is unstable unless you cancelled this yourself.')  # noqa: E501
                print('')
            else:
                print(error)

        def on_close(ws):
            print('CONNECTION CLOSED AT: ' + str(datetime.now().time().strftime('%H:%M:%S')))  # noqa: E501

        def on_open(ws):
            ws_data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "public/auth",
                "params": {
                    "grant_type": "client_signature",
                    "client_id": self.client_id,
                    "timestamp": tstamp,
                    "nonce": nonce,
                    "scope": self.scope,
                    "signature": signature,
                    "data": data}
            }
            ws.send(json.dumps(ws_data))

            # initiating heartbeat
            if self.heartbeat_set_flag == 0 and self.heartbeat_requested_flag == 0:  # noqa: E501
                self.heartbeat_requested_flag = 1
                print('Heartbeat Requested at: ' + str(datetime.now().time().strftime('%H:%M:%S')))  # noqa: E501
                ws_data = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "public/set_heartbeat",
                    "params": {
                        "interval": 10
                    }
                }
                ws.send(json.dumps(ws_data))

        # Detailed Logging
        # websocket.enableTrace(True)

        # Initialize Websocket App
        ws = websocket.WebSocketApp(self.exchange_version,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        ws.on_open = on_open

        ws.run_forever()


if __name__ == "__main__":
    # Your "scope" variable must be 'read-only' or 'read-write'.
    scope = 'read-only'
    # Your "exchange_version" variable must be 'live' or 'testnet'.
    exchange_version = 'testnet'

    # Client Signature Authentication
    tstamp = str(int(time.time()) * 1000)
    data = ''
    nonce = secrets.token_urlsafe(10)
    base_signature_string = tstamp + "\n" + nonce + "\n" + data
    byte_key = Client_Secret.encode()
    message = base_signature_string.encode()
    signature = hmac.new(byte_key, message, hashlib.sha256).hexdigest()

    # Your Trading Engine
    UserWebsocketEngine(client_Id=Client_Id,
                        scope=DeribitAPIAccessScope(scope).designated_scope,
                        exchange_version=DeribitExchangeVersion(exchange_version).exchange_version)  # noqa: E501
