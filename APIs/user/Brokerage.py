from utils.request_connect import v3_mk_request
from utils.load_yaml import load_yaml_file


def get_quote(param, trace_id):
    res = v3_mk_request("POST", "api/3/retail/quote", param, trace_id)
    return res


def execute_trade(param, trace_id):
    res = v3_mk_request('POST', 'api/3/retail/trade', param, trace_id)
    return res

if __name__ == '__main__':
    while True:
        params = {"quoteRequest":
        {"buyTradedCurrency": "true",
        "tradedCurrency": "BTC",
        "settlementCurrency": "USD",
        "tradedCurrencyAmount": 0.00001}}
        res = get_quote(params,'123')
        print('Quote response',res)
        quoteId = res['res']['quoteResponse']['quoteId']
        params = {'tradeRequest': {'quoteId':quoteId}}
        res = execute_trade(params,'123')
        print('Execute response', res)
        print('-'*50)