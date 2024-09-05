import time

import allure
import pytest

from APIs.user.Exchange import create_order, get_order, get_exchange_currency_pairs, get_orderbook, cancel_order
from utils.business_operation.exchange_operation import price_for_limit, fills_price
from utils.decimal_calculation import RTD
from utils.ini_read import read_pytest_ini
from utils.log import logger
from utils.output_data import exchange_data_output

reruns = int(read_pytest_ini('retry', 'global setting'))


class ExchangeOrder:
    def __init__(self):
        self.side = None
        self.orderID = None
        self.create_order_res = None
        self.symbol = None

    @allure.step("Make Exchange order - PostOnly")
    def create_P_PostOnlyOrder(self, params, expected):
        res_dict = create_order(params)
        res = res_dict['res']
        self.create_order_res = res
        try:
            self.symbol = params['symbol']
            assert res['symbol'] == params[
                'symbol'], f"symbol assertion error, response symbol {res['symbol']} != param symbol {params['symbol']}"
            assert RTD(res['orderQty']) == RTD(params[
                                                   'orderQty']), f"symbol assertion error, response orderQty {RTD(res['orderQty'])} != param orderQty {RTD(params['orderQty'])}"
            assert RTD(res['price']) == RTD(params[
                                                'price']), f"price assertion error, response price {RTD(res['price'])} != param price {RTD(params['price'])}"
            assert res['ordType'] == params[
                'ordType'], f"ordType assertion error, response ordType {res['ordType']} != param ordType {params['ordType']}"
            assert res['execInst'] == params[
                'execInst'], f"execInst assertion error, response execInst {res['execInst']} != param execInst {params['execInst']}"
            assert res['side'] == params[
                'side'], f"side assertion error, response side {res['side']} != param side {params['side']}"
            assert res['timeInForce'] == params[
                'timeInForce'], f"timeInForce assertion error, response timeInForce {res['timeInForce']} != param timeInForce {params['timeInForce']}"
            if expected not in ['PartiallyFilled','Filled']:
                assert res['ordStatus'] == expected, f"ordStatus assertion error, response ordStatus {res['ordStatus']} != expected ordStatus {expected}"

            allure.attach(name="Make Exchange Order",
                          body=f"Request:{res_dict['response'].request.body}\nResponse:{res_dict['response'].text}",
                          attachment_type=allure.attachment_type.JSON)
            self.orderID = res['orderID']
            if expected == 'New':
                self.check_order_exist()
            elif expected == 'Withdrawn':
                self.check_order_exist(exist=False)
            return self.orderID
        except AssertionError as e:
            logger.log(
                f'create_P_ex_order Assertion Error：{str(e)}\nRequest:{res_dict["response"].request.body}\nResponse:{res_dict["response"].text}',
                'error')
            allure.attach(name="Make Exchange Order",
                          body=f"Request:{res_dict['response'].request.body}\nResponse:{res_dict['response'].text}",
                          attachment_type=allure.attachment_type.JSON)
            raise e

        except Exception as ex:
            logger.log(
                f'create_P_ex_order Unknow Error：{str(ex)}\nRequest:{res_dict["response"].request.body}\nResponse:{res_dict["response"].text}',
                'critical')
            allure.attach(name="Make Exchange Order",
                          body=f"Request:{res_dict['response'].request.body}\nResponse:{res_dict['response'].text}",
                          attachment_type=allure.attachment_type.JSON)
            raise ex

    @allure.step("Make Exchange order - PostOnly")
    def create_N_PostOnlyOrder(self, params, expected):
        res_dict = create_order(params)
        res = res_dict['res']
        self.create_order_res = res
        try:
            assert res['error'][
                       'message'] == expected, f"Message assertion error, response msg {res['error']['message']} != expected msg {expected}"
            allure.attach(name="Make Exchange Order",
                          body=f"Request:{res_dict['response'].request.body}\nResponse:{res_dict['response'].text}",
                          attachment_type=allure.attachment_type.JSON)
        except AssertionError as e:
            logger.log(
                f'create_N_ex_order Assertion Error：{str(e)}\nRequest:{res_dict["response"].request.body}\nResponse:{res_dict["response"].text}',
                'error')
            allure.attach(name="Make Exchange Order",
                          body=f"Request:{res_dict['response'].request.body}\nResponse:{res_dict['response'].text}",
                          attachment_type=allure.attachment_type.JSON)
            raise e

        except Exception as ex:
            logger.log(
                f'create_N_ex_order Unknow Error：{str(ex)}\nRequest:{res_dict["response"].request.body}\nResponse:{res_dict["response"].text}',
                'critical')
            allure.attach(name="Make Exchange Order",
                          body=f"Request:{res_dict['response'].request.body}\nResponse:{res_dict['response'].text}",
                          attachment_type=allure.attachment_type.JSON)
            raise ex
    @allure.step("Make Exchange order - Market")
    def create_P_MarketOrder(self, params, expected):
        should_fills_price = fills_price(params['side'], self.symbol)
        res_dict = create_order(params)
        res = res_dict['res']
        self.create_order_res = res

        try:
            self.symbol = params['symbol']
            self.side = params['side']
            assert res['symbol'] == params[
                'symbol'], f"symbol assertion error, response symbol {res['symbol']} != param symbol {params['symbol']}"
            assert RTD(res['orderQty']) == RTD(params[
                                                   'orderQty']), f"symbol assertion error, response orderQty {RTD(res['orderQty'])} != param orderQty {RTD(params['orderQty'])}"
            assert res['ordType'] == params[
                'ordType'], f"ordType assertion error, response ordType {res['ordType']} != param ordType {params['ordType']}"

            assert res['side'] == params[
                'side'], f"side assertion error, response side {res['side']} != param side {params['side']}"
            assert res['timeInForce'] == 'GoodTillCancel', f"timeInForce assertion error, response timeInForce {res['timeInForce']} != GoodTillCancel"
            assert res['ordStatus'] == expected, f"ordStatus assertion error, response ordStatus {res['ordStatus']} != expected ordStatus {expected}"

            allure.attach(name="Make Exchange Order",
                          body=f"Request:{res_dict['response'].request.body}\nResponse:{res_dict['response'].text}",
                          attachment_type=allure.attachment_type.JSON)
            self.orderID = res['orderID']
            actual_fills_price = get_order({'orderID': self.orderID, 'open': 'false'})['res'][0]['avgPx']
            assert RTD(should_fills_price) == RTD(actual_fills_price), f"should_fills_price assertion error, should_fills_price {RTD(should_fills_price)} != actual_fills_price {RTD(actual_fills_price)}"

            if expected == 'New':
                self.check_order_exist()
            elif expected == 'Withdrawn':
                self.check_order_exist(exist=False)
            return self.orderID
        except AssertionError as e:
            logger.log(
                f'create_P_MarketOrder Assertion Error：{str(e)}\nRequest:{res_dict["response"].request.body}\nResponse:{res_dict["response"].text}',
                'error')
            allure.attach(name="Make Exchange Order",
                          body=f"Request:{res_dict['response'].request.body}\nResponse:{res_dict['response'].text}",
                          attachment_type=allure.attachment_type.JSON)
            raise e

        except Exception as ex:
            logger.log(
                f'create_P_MarketOrder Unknow Error：{str(ex)}\nRequest:{res_dict["response"].request.body}\nResponse:{res_dict["response"].text}',
                'critical')
            allure.attach(name="Make Exchange Order",
                          body=f"Request:{res_dict['response'].request.body}\nResponse:{res_dict['response'].text}",
                          attachment_type=allure.attachment_type.JSON)
            raise ex

    @allure.step("Check order exist")
    def check_order_exist(self, exist=True):
        if exist:
            params = {
                "open": 'true',
                'orderID': self.orderID
            }
            res_dict = get_order(params)
            res = res_dict['res']
        elif exist is False:
            params = {
                "open": 'false',
                'orderID': self.orderID
            }
            res_dict = get_order(params)
            res = res_dict['res']
        get_orderID = res[0]['orderID']
        assert get_orderID == self.orderID, f"orderID assertion error, response orderID {get_orderID} != param create_order_orderID {self.orderID}"
        allure.attach(name="Check Order Exist",
                      body=f"OrderID {self.orderID}\nRequest:{res_dict['response'].request.body}\nResponse:{res_dict['response'].text}",
                      attachment_type=allure.attachment_type.JSON)

    @allure.step("Get last Price")
    def get_lastPrice(self):
        res = get_exchange_currency_pairs()['res']
        for item in res:
            if item['symbol'] == self.symbol:
                return item['lastPrice']

    @allure.step("Get min asks, max bides")
    def get_asksAndbids(self):
        res = get_orderbook(self.symbol)['res']
        return res['asks'][0][0], res['bids'][0][0]

    @allure.step("Cancel Order")
    def cancel_order(self):
        res_dict = cancel_order(self.orderID)
        res = res_dict['res']
        assert res[0][
                   'orderID'] == self.orderID, f"orderID assertion error, response orderID {res[0]['orderID']} != param cancel_orderID {self.orderID}"
        allure.attach(name="Make Exchange Order",
                      body=f"Request:{res_dict['response'].request.body}\nResponse:{res_dict['response'].text}",
                      attachment_type=allure.attachment_type.JSON)

    @allure.step('Check Fills Order')
    def check_fills_order(self, params_list, expected_list):
        orderID_list = []
        for param, expected in zip(params_list, expected_list):
            logger.log(f'{param}', 'debug')
            orderID = ''
            if 'PostOnly' in param.values():
                orderID = self.create_P_PostOnlyOrder(param, expected)
            elif "Market" in param.values():
                orderID = self.create_P_MarketOrder(param, expected)
            orderID_list.append([orderID, expected])
        for item in orderID_list:
            open = 'true'
            if item[1] == 'Filled':
                open = 'false'
            payload = {'orderID': item[0], "open": open}
            res_dict = get_order(payload)
            res_expected = res_dict['res'][0]['ordStatus']
            assert res_expected == item[
                1], f"Expected assertion error, response res_expected {res_expected} != expected {item[1]}"
            allure.attach(name="Make Exchange Order",
                          body=f"Request:{res_dict['response'].request.body}\nResponse:{res_dict['response'].text}",
                          attachment_type=allure.attachment_type.JSON)

@pytest.mark.usefixtures("exchange_order_before_check")
@pytest.mark.parametrize('case_title,params,expected',
                         exchange_data_output("Exchange/PostOnly/Positive_PostOnly_order"))
@allure.parent_suite("Exchange API TEST")
@allure.suite("PostOnly Test Cases")
@allure.epic('Exchange API TEST')
@allure.feature("PostOnly Test Cases")
@allure.title("{case_title}")
@pytest.mark.flaky(reruns=reruns, reason='None')
def test_PostOnly_Positive_ExchangeOrder(case_title, params, expected):
    allure.dynamic.story(f"Positive Test Cases")
    allure.dynamic.sub_suite(f"Positive Test Cases")
    try:
        logger.log(f'{case_title}', 'debug')
        client = ExchangeOrder()
        client.create_P_PostOnlyOrder(params, expected)
    except AssertionError or Exception as e:
        # 如果失败，等待一段时间再重试
        time.sleep(2)  # 等待 2 秒
        raise e


@pytest.mark.usefixtures("exchange_order_before_check")
@pytest.mark.parametrize('case_title,params,expected',
                         exchange_data_output("Exchange/PostOnly/Negative_PostOnly_order"))
@allure.parent_suite("Exchange API TEST")
@allure.suite("PostOnly Test Cases")
@allure.epic('Exchange API TEST')
@allure.feature("PostOnly Test Cases")
@allure.title("{case_title}")
@pytest.mark.flaky(reruns=reruns, reason='None')
def test_PostOnly_Negative_ExchangeOrder(case_title, params, expected):
    allure.dynamic.story(f"Negative Test Cases")
    allure.dynamic.sub_suite(f"Negative Test Cases")
    try:
        logger.log(f'{case_title}', 'debug')
        client = ExchangeOrder()
        client.create_N_PostOnlyOrder(params, expected)
    except AssertionError or Exception as e:
        # 如果失败，等待一段时间再重试
        time.sleep(2)  # 等待 2 秒
        raise e


@pytest.mark.usefixtures("exchange_order_before_check")
@pytest.mark.parametrize('case_title,params,expected',
                         exchange_data_output("Exchange/PostOnly/Cancel_PostOnly_order"))
@allure.parent_suite("Exchange API TEST")
@allure.suite("PostOnly Test Cases")
@allure.epic('Exchange API TEST')
@allure.feature("PostOnly Test Cases")
@allure.title("{case_title}")
@pytest.mark.flaky(reruns=reruns, reason='None')
def test_PostOnly_CancelOrder(case_title, params, expected):
    allure.dynamic.story(f"Cancel Order Test Cases")
    allure.dynamic.sub_suite(f"Cancel Order Test Cases")
    try:
        logger.log(f'{case_title}', 'debug')
        client = ExchangeOrder()
        client.create_P_PostOnlyOrder(params, expected)
        client.cancel_order()
    except AssertionError or Exception as e:
        # 如果失败，等待一段时间再重试
        time.sleep(2)  # 等待 2 秒
        raise e


@pytest.mark.usefixtures("exchange_order_before_check")
@pytest.mark.parametrize('case_title, params_list, expected_list,execute_type',
                         exchange_data_output("Exchange/PostOnly/PostOnly_order_fills"))
@allure.parent_suite("Exchange API TEST")
@allure.suite("PostOnly Test Cases")
@allure.epic('Exchange API TEST')
@allure.feature("PostOnly Test Cases")
@allure.title("{case_title}")
@pytest.mark.flaky(reruns=reruns, reason='None')
def test_PostOnly_FillsOrder(case_title, params_list, expected_list, execute_type):
    allure.dynamic.story(f"{execute_type} Test Cases")
    allure.dynamic.sub_suite(f"{execute_type} Test Cases")
    try:
        logger.log(f'{case_title}', 'debug')
        client = ExchangeOrder()
        client.check_fills_order(params_list, expected_list)

    except AssertionError or Exception as e:
        # 如果失败，等待一段时间再重试
        time.sleep(2)  # 等待 2 秒
        raise e
