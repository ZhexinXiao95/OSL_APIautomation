import time

import allure
import pytest

from APIs.user.Exchange import create_order, get_order
from utils.ini_read import read_pytest_ini
from utils.log import logger
from utils.output_data import exchange_data_output

reruns = int(read_pytest_ini('retry', 'global setting'))


class ExchangeOrder:
    def __init__(self):
        self.orderID = None
        self.create_order_res = None

    @allure.step("Make Exchange order - PostOnly")
    def create_ex_order(self, params):
        res = create_order(params)
        self.create_order_res = res
        self.orderID = res['res']['orderID']
        try:
            assert res['symbol'] == params[
                'symbol'], f"symbol assertion error, response symbol {res['symbol']} != param symbol {params['symbol']}"
            assert res['orderQty'] == params[
                'orderQty'], f"symbol assertion error, response orderQty {res['orderQty']} != param orderQty {params['orderQty']}"
            assert res['price'] == params[
                'price'], f"price assertion error, response price {res['price']} != param price {params['price']}"
            assert res['ordType'] == params[
                'ordType'], f"ordType assertion error, response ordType {res['ordType']} != param ordType {params['ordType']}"
            assert res['execInst'] == params[
                'execInst'], f"execInst assertion error, response execInst {res['execInst']} != param execInst {params['execInst']}"
            assert res['side'] == params[
                'side'], f"side assertion error, response side {res['side']} != param side {params['side']}"
            assert res['timeInForce'] == params[
                'timeInForce'], f"timeInForce assertion error, response timeInForce {res['timeInForce']} != param timeInForce {params['timeInForce']}"

            allure.attach(name="Make Exchange Order",
                          body=f"Request:{res['response'].request.body}\nResponse:{res['response'].text}",
                          attachment_type=allure.attachment_type.JSON)
            self.check_order_exist()
            return self.orderID
        except AssertionError as e:
            logger.log(
                f'quote_request Assertion Error：{str(e)}\nRequest:{res["response"].request.body}\nResponse:{res["response"].text}',
                'error')
            allure.attach(name="Make Exchange Order",
                          body=f"Request:{res['response'].request.body}\nResponse:{res['response'].text}",
                          attachment_type=allure.attachment_type.JSON)
            raise e

        except Exception as ex:
            logger.log(
                f'quote_request Unknow Error：{str(ex)}\nRequest:{res["response"].request.body}\nResponse:{res["response"].text}',
                'critical')
            allure.attach(name="Make Exchange Order",
                          body=f"Request:{res['response'].request.body}\nResponse:{res['response'].text}",
                          attachment_type=allure.attachment_type.JSON)
            raise ex

    def check_order_exist(self):
        res = get_order(None)
        get_orderID = res['res'][0]['orderID']
        assert get_orderID == self.orderID, f"orderID assertion error, response orderID {get_orderID} != param create_order_orderID {self.orderID}"
        allure.attach(name="Check Order Exist",
                      body=f"OrderID {self.orderID}\nRequest:{res['response'].request.body}\nResponse:{res['response'].text}",
                      attachment_type=allure.attachment_type.JSON)
PostOnly_testdata = read_pytest_ini('exchange_datafile', 'global setting')


@pytest.mark.usefixtures("exchange_order_before_check")
@pytest.mark.parametrize('case_type,case_title,params',
                         exchange_data_output(PostOnly_testdata))
@allure.parent_suite("Exchange API TEST")
@allure.suite("PostOnly Test Cases")
@allure.epic('Exchange API TEST')
@allure.feature("exchange_data_output Test Cases")
@allure.title("{case_title}")
@pytest.mark.flaky(reruns=reruns, reason='None')
def test_makeExchangeOrder(case_type, case_title, params):
    allure.dynamic.story(f"{case_type} Test Cases")
    allure.dynamic.sub_suite(f"{case_type} Test Cases")
    logger.log(case_type)
    try:
        client = ExchangeOrder()
        client.create_ex_order(params)
    except AssertionError or Exception as e:
        # 如果失败，等待一段时间再重试
        time.sleep(2)  # 等待 2 秒
        raise e
