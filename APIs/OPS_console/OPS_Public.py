from APIs.OPS_console.OPS_APIs import OPS_API
from utils.ini_read import read_pytest_ini
from utils.log import logger
from utils.path_concatenation import get_concatenation
from utils.request_connect import make_request


class OpsPublic(OPS_API):
    def listUser(self, account):
        data = {
            "limit": 20,
            "loginUsernameSearchText": account,
        }
        path = "/opUser/listUser" + get_concatenation(data)
        response = make_request('get', path=self.host + path, headers=self.headers_auth)

        site = read_pytest_ini('site', 'global setting').upper()
        for value in response:
            if site in value['siteGroup']:
                uuid = value['uuid']
        if uuid:
            return uuid
        else:
            logger.log(f'cannot find the uuid for {account}')

    def fiat_deposit(self):
        pass

    def account_balance(self, userUuid, currency, wallet='availableBalance', limit=100):
        data = {
            "userUuid": userUuid,
            'accountGroupUuid': userUuid,
            'ccy': currency,
            "limit": limit,
        }
        path = "/Account" + get_concatenation(data)
        response = make_request('get', path=self.host + path, headers=self.headers_auth)
        return response[0][wallet]

if __name__ == '__main__':
    # print(OpsPublic().listUser('shawn.xiao@osl.com'))
    OpsPublic().account_balance('a59ff04c-6be3-4de9-88dd-7a8fde018ff6', 'BTC')