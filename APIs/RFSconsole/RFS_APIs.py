import copy

import allure
import requests

from APIs.user.Brokerage import get_quote, execute_trade
from utils.Authenticator import authenticator_code
from utils.ini_read import read_pytest_ini, write_pytest_ini
from utils.request_connect import make_request


class RFS_API:
    def __init__(self, env):
        self.env = env
        self.host = read_pytest_ini('rfs_console_host', self.env)
        self.token = read_pytest_ini('rfs_console_token', self.env)
        self.cookie = read_pytest_ini("rfs_console_cookie", self.env)
        auth = read_pytest_ini("rfs_console_acct", self.env)
        self.account, self.pwd = auth[0], auth[1]
        self.headers = {
            'content-type': 'application/json',
            'cookie': self.cookie,
            'Token': self.token,
        }

    @allure.step("rfs_authToken")
    def rfs_authToken(self):
        current_otp = authenticator_code('rfs_console_authenticator', self.env)
        headers = copy.deepcopy(self.headers)
        del headers['Token']
        path = "/ui/auth"
        data = {
            "username": self.account,
            "password": self.pwd,
            "otp": current_otp
        }
        response = make_request('post', path=self.host + path, params=data, headers=headers)
        write_pytest_ini('rfs_console_token', self.env, response['authToken'])
        return response['authToken']

    @allure.step("rfs_status")
    def status(self):
        path = "/trading/status"
        response = make_request('get', path=self.host + path, headers=self.headers)
        return response

    @allure.step("rfs_status_venue")
    def status_venue(self):
        path = "/ui/status-venue"
        response = make_request('get', path=self.host + path, headers=self.headers)
        return response

    @allure.step("rfs_trades_completed")
    def trades_completed(self, page=0):
        path = f"/trade/client-trades/completed?page={page}"
        data = {'startDate': '2024-07-22 08:32:47',
                }
        response = make_request('post', path=self.host + path, params=data, headers=self.headers)
        assert response['success'] is True, f'trades_completed response error {response}'
        return response

    @allure.step("rfs_trades_indeterminateOrpending")
    def trades_indeterminateOrpending(self, page=0):
        path = f"/trade/client-trades/pending?page={page}"
        data = {'status': "",
                }
        response = make_request('post', path=self.host + path, params=data, headers=self.headers)
        assert response['success'] is True, f'trades_completed response error {response}'
        return response

    @allure.step("rfs_aggregated_positions")
    def aggregated_positions(self):
        path = "/trade/api/rfsAggregatedPosition"
        headers = copy.deepcopy(self.headers)
        headers['authorization'] = headers.pop('Token', self.token)
        response = make_request('get', path=self.host + path, headers=headers)
        return response

    @allure.step("rfs_cc_pair_status")
    def cc_pair_status(self):
        path = "/trading/all-ccy-pair-status"
        response = make_request('get', path=self.host + path, headers=self.headers)
        return response

    @allure.step('turn on venus')
    def turn_on_venus(self, venus):
        path = f"/ui/connect-venue?venue={venus}"
        response = make_request('get', path=self.host + path, headers=self.headers)
        return response

    @allure.step('turn off venus')
    def turn_off_venus(self, venus):
        path = f"/ui/disconnect-venue?venue={venus}"
        response = make_request('get', path=self.host + path, headers=self.headers)
        return response



if __name__ == '__main__':
    RFS = RFS_API('stage')
    print(RFS.rfs_authToken())
    a = RFS.turn_on_venus('OSL')
    print(a)
    print(a['success'])
    # print(RFS.status())
    # print(RFS.status_venue())
    # print(RFS.trades_indeterminateOrpending())
    # print(RFS.aggregated_positions())
    # print(RFS.cc_pair_status())


