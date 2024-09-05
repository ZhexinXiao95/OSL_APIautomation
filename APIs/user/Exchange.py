import allure

from utils.log import logger
from utils.request_connect import v4_mk_request


def get_exchange_currency_pairs():
    try:
        res = v4_mk_request('GET', '/api/v4/instrument')
        return res
    except Exception as ex:
        logger.log(f'get_currency_pairs unknow error：{str(ex)}', 'critical')


def create_order(params):
    """
    https://osl.com/reference/create-new-order
    :param params:
    :return:
    """
    try:
        res = v4_mk_request('POST', '/api/v4/order', params)
        return res
    except Exception as ex:
        logger.log(f'create_order unknow error：{str(ex)}', 'critical')


def cancel_order(orderID):
    """
    https://osl.com/reference/cancel-orders
    :param orderID:
    :return:
    """
    try:
        params = {
            "orderID": [orderID]
        }
        res = v4_mk_request('DELETE', '/api/v4/order', params)
        return res
    except Exception as ex:
        logger.log(f'cancel_order unknow error：{str(ex)}', 'critical')


@allure.step("clear existing order")
def cancel_all_order(params):
    """
    https://osl.com/reference/cancel-all-orders
    :param params:
    :return:
    """
    try:
        res = v4_mk_request('DELETE', '/api/v4/order/all', params, need_res=False)
        assert res.status_code in [200, 204], f'assertion error, got {res.status_code}'
        logger.log(f'cancel_all_order success, got {res.status_code}')
    except Exception as ex:
        logger.log(f'cancel_all_order unknow error：{str(ex)}', 'critical')


def get_order(params):
    """
    https://osl.com/reference/get-orders
    :param params:
    :return:
    """
    try:
        res = v4_mk_request('GET', '/api/v4/order', params)
        return res
    except Exception as ex:
        logger.log(f'get_order unknow error：{str(ex)}', 'critical')


def get_execution(params):
    """
    https://osl.com/reference/get-executions
    :param params:
    :return:
    """
    try:
        res = v4_mk_request('GET', '/api/v4/execution', params)
        return res
    except Exception as ex:
        logger.log(f'get_execution unknow error：{str(ex)}', 'critical')


def get_execution_an_order(params):
    """
    https://osl.com/reference/get-executions-of-order
    :param params:
    :return:
    """
    try:
        res = v4_mk_request('GET', '/api/v4/execution/order', params)
        return res
    except Exception as ex:
        logger.log(f'get_execution_an_order unknow error：{str(ex)}', 'critical')


def get_orderbook(symbol, depth=10):
    """
    https://osl.com/reference/get-order-book
    :param symbol:
    :param depth:
    :return:
    """
    try:
        res = v4_mk_request('GET', f'/api/v4/orderBook/L2?symbol={symbol}&depth={depth}')
        return res
    except Exception as ex:
        logger.log(f'get_orderbook unknow error：{str(ex)}', 'critical')


def get_exchange_wallet(params):
    """
    https://osl.com/reference/get-exchange-wallet
    :param params:
    :return:
    """
    try:
        res = v4_mk_request('GET', '/api/v4/user/wallet', params)
        return res
    except Exception as ex:
        logger.log(f'get_exchange_wallet unknow error：{str(ex)}', 'critical')


def get_exchange_trade_list(params):
    """
    https://osl.com/reference/get-exchange-trade-list
    :param params:
    :return:
    """
    try:
        res = v4_mk_request('GET', '/api/v4/trade', params)
        return res
    except Exception as ex:
        logger.log(f'get_exchange_trade_list unknow error：{str(ex)}', 'critical')


if __name__ == '__main__':
    # get_exchange_currency_pairs()
    # params = {
    #     'ordType': 'Limit',
    #     'symbol': 'BTCUSD',
    #     'orderQty': '1',
    #     'price': '69500',
    #     'side': 'Buy'
    # }
    # create_order(params)
    # params = None
    # get_order(params)
    # params = {
    #     "symbol": "BTCUSD"
    # # }
    # cancel_all_order(None)
    #
    post_only_params = {
        "symbol": "BTCUSD",
        "orderQty": "0.01",
        "side": "Buy",
        "ordType": "Limit",
        "price": '50000',
        "timeInForce": "GoodTillCancel",
        'execInst': 'PostOnly'
    }

    orderID = create_order(post_only_params)['res']['orderID']
    # print(orderID)
    # get_order(None)
    # print(get_exchange_currency_pairs())
    # res = get_orderbook('BTCUSD')['res']
    # print(res['asks'][0][0])
    cancel_order(orderID)
