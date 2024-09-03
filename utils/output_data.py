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


if __name__ == '__main__':
    print(rfq_data_output('get_quote(IPA_Gateway_Test)Test_9'))