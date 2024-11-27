from decimal import Decimal

import allure

from utils.log import logger
from utils.request_connect import v3_mk_request

@allure.step("get_account_information")
def get_account_information(currency=None, wallet='Wallets', account='Brokerage_Available_Balance', multiple=True):
    dict = {}
    try:
        res = v3_mk_request('GET', 'api/3/account', log=False)
        if currency is None:
            return res['res']
        elif multiple is False:
            return res['res']['data'][wallet][currency][account]['value']
        else:
            for cur in currency:
                value = res['res']['data'][wallet][cur][account]['value']
                dict[cur] = Decimal(value)
            return dict
    except Exception as ex:
        logger.log(f'get_account_information 发生未知异常：{str(ex)} \nres:{res}', 'critical')


@allure.step("get_transaction_list")
def get_transaction_list(max=None):
    param = {
        'lang': 'en-US',
        'max': 50
    }
    if max:
        param['max'] = max
    try:
        res = v3_mk_request('GET', 'api/3/transaction/list', param)
        return res['res']
    except Exception as ex:
        logger.log(f'get_transaction_list unknow error：{str(ex)}', 'critical')

if __name__ == '__main__':
    print(get_account_information(currency='BTC',multiple=False))
    # print(get_transaction_list())