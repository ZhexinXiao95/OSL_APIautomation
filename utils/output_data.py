from utils.business_operation.exchange_operation import price_for_limit
from utils.load_yaml import load_yaml_file
from utils.log import logger


def rfq_data_output(file):
    data_list = load_yaml_file(file)
    list = []
    try:
        for data in data_list:
            case_title = data['case_title']
            if 'expected' in data['quoteRequest']:
                quoteRequest_expected = data['quoteRequest']['expected']
                del data['quoteRequest']['expected']
            quoteRequest = {}
            quoteRequest['quoteRequest'] = data['quoteRequest']
            if 'expected' in data['tradeRequest']:
                tradeRequest_expected = data['tradeRequest']['expected']
                del data['tradeRequest']['expected']
            case_type = data['case_type']
            data = case_type, case_title, quoteRequest, quoteRequest_expected, tradeRequest_expected
            list.append(data)
        return list
    except Exception as ex:
        logger.log(f'output_yaml Unknow Error {ex}\n{data}')
        raise ex


def exchange_data_output(file):
    data_list = load_yaml_file(file)
    list = []
    try:
        for data in data_list:
            case_title = data['case_title']
            if "Orders" in data:
                execute_type = data['execute_type']
                params_list = []
                expected_list = []
                for req in data['Orders']:
                    # 成交单 - 替换价格变量
                    params = req['request']
                    # Market单不需要price
                    if params['ordType'] != 'Market':
                        order_price = price_for_limit(params['side'], params['symbol'])
                        params['price'] = order_price

                    expected = req['expected']
                    params_list.append(params)
                    expected_list.append(expected)
                data = case_title, params_list, expected_list, execute_type

            else:
                # case_type = data['case_type']
                params = data['request']
                expected = data['expected']
                data = case_title, params, expected
            list.append(data)
        return list
    except Exception as ex:
        logger.log(f'output_yaml Unknow Error {ex}\n{data}')
        raise ex


if __name__ == '__main__':
    # print(rfq_data_output('/RFQ/test_sol'))
    print(exchange_data_output('Exchange/create_PostOnly_order'))
