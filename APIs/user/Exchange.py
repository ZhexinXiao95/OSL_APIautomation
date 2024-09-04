from utils.log import logger
from utils.request_connect import v3_mk_request


def get_exchange_currency_pairs():
    try:
        res = v3_mk_request('GET', '/api/v4/instrument')
        return res['res']
    except Exception as ex:
        logger.log(f'get_currency_pairs unknow error：{str(ex)}', 'critical')


def create_order(params):
    """
    https://osl.com/reference/create-new-order
    :param params:
    :return:
    """
    try:
        res = v3_mk_request('POST', '/api/v4/order', params)
        return res['res']
    except Exception as ex:
        logger.log(f'create_order unknow error：{str(ex)}', 'critical')


def cancel_order(params):
    """
    https://osl.com/reference/cancel-orders
    :param params:
    :return:
    """
    try:
        res = v3_mk_request('DELETE', '/api/v4/order', params)
        return res['res']
    except Exception as ex:
        logger.log(f'cancel_order unknow error：{str(ex)}', 'critical')


def cancel_all_order(params):
    """
    https://osl.com/reference/cancel-all-orders
    :param params:
    :return:
    """
    try:
        res = v3_mk_request('DELETE', '/api/v4/order/all', params)
        return res['res']
    except Exception as ex:
        logger.log(f'cancel_all_order unknow error：{str(ex)}', 'critical')


def get_order(params):
    """
    https://osl.com/reference/get-orders
    :param params:
    :return:
    """
    try:
        res = v3_mk_request('GET', '/api/v4/order', params)
        return res['res']
    except Exception as ex:
        logger.log(f'get_order unknow error：{str(ex)}', 'critical')

def get_execution(params):
    """
    https://osl.com/reference/get-executions
    :param params:
    :return:
    """
    try:
        res = v3_mk_request('GET', '/api/v4/execution', params)
        return res['res']
    except Exception as ex:
        logger.log(f'get_execution unknow error：{str(ex)}', 'critical')

def get_execution_an_order(params):
    """
    https://osl.com/reference/get-executions-of-order
    :param params:
    :return:
    """
    try:
        res = v3_mk_request('GET', '/api/v4/execution/order', params)
        return res['res']
    except Exception as ex:
        logger.log(f'get_execution_an_order unknow error：{str(ex)}', 'critical')


def get_orderbook(params):
    """
    https://osl.com/reference/get-order-book
    :param params:
    :return:
    """
    try:
        res = v3_mk_request('GET', '/api/v4/orderBook/L2', params)
        return res['res']
    except Exception as ex:
        logger.log(f'get_orderbook unknow error：{str(ex)}', 'critical')

def get_exchange_wallet(params):
    """
    https://osl.com/reference/get-exchange-wallet
    :param params:
    :return:
    """
    try:
        res = v3_mk_request('GET', '/api/v4/user/wallet', params)
        return res['res']
    except Exception as ex:
        logger.log(f'get_exchange_wallet unknow error：{str(ex)}', 'critical')

def get_exchange_trade_list(params):
    """
    https://osl.com/reference/get-exchange-trade-list
    :param params:
    :return:
    """
    try:
        res = v3_mk_request('GET', '/api/v4/trade', params)
        return res['res']
    except Exception as ex:
        logger.log(f'get_exchange_trade_list unknow error：{str(ex)}', 'critical')