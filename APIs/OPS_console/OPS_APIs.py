import copy

import allure
from utils.Authenticator import authenticator_code
from utils.ini_read import read_pytest_ini, write_pytest_ini
from utils.request_connect import make_request


class OPS_API:
    def __init__(self, env):
        self.env = env
        self.host = read_pytest_ini('ops_console_host', self.env)
        self.token = read_pytest_ini('ops_console_token', self.env)
        self.cookie = read_pytest_ini("ops_console_cookie", self.env)
        auth = read_pytest_ini("ops_console_acct", self.env)
        self.account, self.pwd = auth[0], auth[1]
        self.headers = {
            'content-type': 'application/json',
            'cookie': self.cookie,
            'Token': self.token,
        }

    @allure.step("ops_authToken")
    def ops_authToken(self):
        current_otp = authenticator_code('ops_console_authenticator', self.env)
        headers = copy.deepcopy(self.headers)
        del headers['Token']
        path = "/auth/api/1.0/login"
        data = {
            "username": self.account,
            "password": self.pwd,
            "otp": current_otp
        }
        response = make_request('post', path=self.host + path, params=data, headers=headers)
        write_pytest_ini('ops_console_token', self.env, response['authToken'])
        return response['authToken']

    @allure.step("ops_transaction")
    def ops_transaction(self, tradeId):
        path = "/Transaction"
        headers = copy.deepcopy(self.headers)
        del headers['Token']
        headers['cookie'] = headers['cookie'] + '; Authorization=' + self.token
        data = {
            'tradeRef': tradeId
        }
        print(headers['cookie'])
        response = make_request('get', path=self.host + path, params=data, headers=headers)
        return response

if __name__ == '__main__':
    OPS = OPS_API('stage')
    print(OPS.ops_authToken())
    print(OPS.ops_transaction('33d04ef55e074889b64d1b06ad4beb26'))
