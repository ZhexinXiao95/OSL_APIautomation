from utils.log import logger
from utils.request_connect import v3_mk_request


def get_currency_pairs():
    try:
        res = v3_mk_request('GET', '/api/3/currencyStatic')
        return res['res']
    except Exception as ex:
        logger.log(f'get_currency_pairs unknow error：{str(ex)}', 'critical')



if __name__ == '__main__':
    print(get_currency_pairs())
