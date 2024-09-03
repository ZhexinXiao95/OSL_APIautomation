import copy
import random
from decimal import Decimal

import pytest
import allure

from APIs.RFSconsole.RFS_APIs import RFS_API
from APIs.user.Brokerage import get_quote, execute_trade
from utils.RFQ_relates_function import brokerage_balance_order_before_check, brokerage_balance_order_after_check, \
    quote_execute_apiDetail_assert, check_ccy_pair, check_user_transaction, check_RFS_console_transaction, \
    assertion_ops_transaction_RFQ
from utils.output_data import rfq_data_output
from utils.request_connect import *
from utils.log import logger

env = read_pytest_ini('env', 'global setting')
reruns = int(read_pytest_ini('retry', 'global setting'))


class RFQorder:
    def __init__(self):
        self.rate = None
        self.trade_amount = None
        self.aggregated_balance_dic = None
        self.hedge_amount = None
        self.trade_id = None
        self.trace_id = generate_traceid()
        self.quote_id = None
        self.case_title = None
        self.quote_res = None
        self.execute_res = None
        self.before_balance_dict = None

    @allure.step("Asking QuoteId Request")
    def quote_request(self, quote_param, quote_expected):
        quote_res = get_quote(quote_param, self.trace_id)
        try:
            assert quote_res[
                       'response'].status_code == 200, f"Expected status code 200, but got {quote_res['response'].status_code}"
            assert quote_expected == quote_res['res']['quoteResponse'][
                'responseCode'], f'quote api did not {quote_expected}'
            # Record quoteId - Assertion between request and response details of Quote API
            assert quote_res['res']['quoteResponse']['quoteId'], f"quoteId did not return"
            quote_param = quote_param['quoteRequest']
            assert quote_param['buyTradedCurrency'] == quote_res['res']['quoteResponse'][
                'buyTradedCurrency'], f"Quote Request {quote_param['buyTradedCurrency']} != Quote Response {quote_res['res']['quoteResponse']['buyTradedCurrency']}"
            assert quote_param['settlementCurrency'] == quote_res['res']['quoteResponse'][
                'settlementCurrency'], f"Quote Request {quote_param['settlementCurrency']} != Quote Response {quote_res['res']['quoteResponse']['settlementCurrency']}"
            assert quote_param['tradedCurrency'] == quote_res['res']['quoteResponse'][
                'tradedCurrency'], f"Quote Request {quote_param['tradedCurrencyAmount']} != Quote Response {quote_res['res']['quoteResponse']['tradedCurrency']}"
            if 'tradedCurrencyAmount' in quote_param:
                assert str(quote_param['tradedCurrencyAmount']) == quote_res['res']['quoteResponse'][
                    'quotedTradedCurrencyAmount'], f"Quote Request {str(quote_param['tradedCurrencyAmount'])} != Quote Response {quote_res['res']['quoteResponse']['quotedTradedCurrencyAmount']}"
            elif 'settlementCurrencyAmount' in quote_param:
                assert str(quote_param['settlementCurrencyAmount']) == quote_res['res']['quoteResponse'][
                    'quotedSettlementCurrencyAmount'], f"Quote Request {str(quote_param['settlementCurrencyAmount'])} != Quote Response {quote_res['res']['quoteResponse']['quotedSettlementCurrencyAmount']}"
            self.quote_id = quote_res['res']['quoteResponse']['quoteId']
            self.quote_res = quote_res
            allure.attach(name="Asking QuoteId Details",
                          body=f"Request:{quote_res['response'].request.body}\nResponse:{quote_res['response'].text}",
                          attachment_type=allure.attachment_type.JSON)
            return self.quote_id
        except AssertionError as e:
            logger.log(
                f'quote_request Assertion Error：{str(e)}\nRequest:{quote_res["response"].request.body}\nResponse:{quote_res["response"].text}',
                'error')
            allure.attach(name="Asking QuoteId Details",
                          body=f"Request:{quote_res['response'].request.body}\nResponse:{quote_res['response'].text}",
                          attachment_type=allure.attachment_type.JSON)
            raise e
        except Exception as ex:
            logger.log(
                f'quote_request Unknow Error：{str(ex)}\nRequest:{quote_res["response"].request.body}\nResponse:{quote_res["response"].text}',
                'critical')
            allure.attach(name="Asking QuoteId Details",
                          body=f"Request:{quote_res['response'].request.body}\nResponse:{quote_res['response'].text}",
                          attachment_type=allure.attachment_type.JSON)
            raise ex

    @allure.step("Make Execute Request")
    def execute_request(self, execute_expected):
        execute_param_ = {'tradeRequest': {}}
        execute_param_['tradeRequest']['quoteId'] = self.quote_id
        try:
            execute_res = execute_trade(execute_param_, self.trace_id)
            self.execute_res = execute_res
            assert execute_res[
                       'response'].status_code == 200, f"Expected status code 200, but got {execute_res['response'].status_code}"
            assert execute_res['res']['tradeResponse'][
                       'responseCode'] == execute_expected, f'execute api did not {execute_expected}'
            self.trade_id = execute_res['res']['tradeResponse']['tradeId']
            allure.attach(name="Make Execute Details",
                          body=f"Request:{execute_res['response'].request.body}\nResponse:{execute_res['response'].text}",
                          attachment_type=allure.attachment_type.JSON)
        except AssertionError as e:
            logger.log(
                f'execute_request Assertion Error：{str(e)}\nRequest:{execute_res["response"].request.body}\nResponse:{execute_res["response"].text}',
                'error')
            self.check_money_lost()
            allure.attach(name="Make Execute Details",
                          body=f"Request:{execute_res['response'].request.body}\nResponse:{execute_res['response'].text}",
                          attachment_type=allure.attachment_type.JSON)
            raise e
        except Exception as ex:
            logger.log(
                f'execute_request Unknow Error：{str(ex)}\nRequest:{execute_res["response"].request.body}\nResponse:{execute_res["response"].text}',
                'critical')
            self.check_money_lost()
            allure.attach(name="Make Execute Details",
                          body=f"Request:{execute_res['response'].request.body}\nResponse:{execute_res['response'].text}",
                          attachment_type=allure.attachment_type.JSON)
            raise ex

    @allure.step("Check Balance Before Trade")
    def check_before_trade(self):
        try:
            self.before_balance_dict = brokerage_balance_order_before_check(self.quote_res)
        except Exception as ex:
            logger.log(f'check_before_trade Unknow Error：{str(ex)}', 'critical')
            raise ex

    @allure.step("Check Balance After Trade")
    def check_after_trade(self):
        try:
            brokerage_balance_order_after_check(self.execute_res, self.before_balance_dict)
        except Exception as ex:
            logger.log(f'check_after_trade Unknow Error：{str(ex)}', 'critical')
            raise ex

    @allure.step("Compare Quote And Execute API Response Details")
    def compare_quote_execute_details(self):
        try:
            quote_execute_apiDetail_assert(self.quote_res, self.execute_res)
        except Exception as ex:
            logger.log(f'compare_quote_execute_details Unknow Error：{str(ex)}', 'critical')
            raise ex

    @allure.step("Execute Fail and Check if money lost")
    def check_money_lost(self):
        try:
            after_balance_dict = brokerage_balance_order_before_check(self.quote_res)
            assert after_balance_dict == self.before_balance_dict, f'after_balance:{after_balance_dict} != before_balance{self.before_balance_dict}'
        except AssertionError as e:
            logger.log(f'check_money_lost Assertion Error：{str(e)}', 'critical')

    @allure.step("check_user_transaction")
    def check_user_tran(self):
        check_user_transaction(self.execute_res['res']['tradeResponse'])

    @allure.step("record aggregated_balance_before trade")
    def check_aggregated_balance_dic_before_trade(self):
        aggregated_balance_dic = RFS_API(env).aggregated_positions()
        self.aggregated_balance_dic = aggregated_balance_dic
    
    @allure.step("check_RFS_console_transaction")
    def check_RFS_console_tran(self):
        self.hedge_amount, self.trade_amount, self.rate = check_RFS_console_transaction(self.quote_res['res']['quoteResponse'], self.execute_res['res']['tradeResponse'], self.aggregated_balance_dic)

    @allure.step("assertion_ops_transaction_RFQ")
    def assertion_ops_tran_RFQ(self):
        assertion_ops_transaction_RFQ(self.trade_id, self.execute_res['res']['tradeResponse'], self.hedge_amount, self.trade_amount, self.rate)

testdata = read_pytest_ini('dataFile','global setting')
@pytest.mark.usefixtures("rfq_order_before_check")
@pytest.mark.parametrize('case_type,case_title,quote_param,quote_expected,execute_expected',
                         rfq_data_output(testdata))
@allure.parent_suite("RFQ API TEST")
@allure.suite("IPA Test Cases")
@allure.epic('RFQ API TEST')
@allure.feature("IPA Test Cases")
@allure.title("{case_title}")
@pytest.mark.flaky(reruns=reruns, reason='Quote Or Execute may Fail')
def test_makeRFQorder(case_type, case_title, quote_param, quote_expected, execute_expected):
    allure.dynamic.story(f"{case_type} Test Cases")
    allure.dynamic.sub_suite(f"{case_type} Test Cases")
    logger.log(case_type)
    try:
        check_ccy_pair(quote_param)
        client = RFQorder()
        client.check_aggregated_balance_dic_before_trade()
        client.quote_request(quote_param, quote_expected)
        client.check_before_trade()
        client.execute_request(execute_expected)
        client.compare_quote_execute_details()
        client.check_after_trade()
        client.check_user_tran()
        client.check_RFS_console_tran()
        client.assertion_ops_tran_RFQ()

    except AssertionError or Exception as e:
        # 如果失败，等待一段时间再重试
        time.sleep(2)  # 等待 2 秒
        raise e
