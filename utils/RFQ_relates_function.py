import allure
from collections import defaultdict

from APIs.OPS_console.OPS_APIs import OPS_API
from APIs.RFSconsole.RFS_APIs import RFS_API
from APIs.user.Custody import get_account_information, get_transaction_list
from utils.decimal_calculation import *
from utils.ini_read import read_pytest_ini
from utils.log import logger
from decimal import Decimal

env = read_pytest_ini('env','global setting')
gateway = read_pytest_ini('rfs_gateway', env)
check_LP = read_pytest_ini('test_LP', 'global setting')


@allure.step("brokerage_balance_order_before_check")
def brokerage_balance_order_before_check(res):
    '''
    Check balance depends on the currency needs before making execute
    :param res: quote_res
    :return: a dict included some information about this trade and balance of the currencies needs
    '''
    logger.log('<===== brokerage_balance_order_before_check start =====>')
    try:
        if 'quoteResponse' in res['res'] and res['res']['quoteResponse']['responseCode'] == 'FULL_QUOTE':
            res = res['res']['quoteResponse']
            side = res['buyTradedCurrency']
            tradedCurrency = res['tradedCurrency']
            settlementCurrency = res['settlementCurrency']
            tradedCurrencyAmount = res['quotedTradedCurrencyAmount']
            quotedSettlementCurrencyAmount = res['quotedSettlementCurrencyAmount']
            executedPrice = res['executedPrice']
            tradedCurrency_balance = get_account_information(currency=tradedCurrency, multiple=False)
            settlementCurrency_balance = get_account_information(currency=settlementCurrency, multiple=False)
            if side:
                logger.log(f'[Quote buy] before order balance : [{tradedCurrency_balance}] | {tradedCurrency}\n'
                           f'[Quote buy] before order balance : [{settlementCurrency_balance}] | {settlementCurrency}')
                # print(f'[Quote buy] before order balance : [{tradedCurrency_balance}] | {tradedCurrency}\n'
                # f'[Quote buy] before order balance : [{settlementCurrency_balance}] | {settlementCurrency}')
            else:
                logger.log(f'[Quote sell] before order balance : [{tradedCurrency_balance}] | {tradedCurrency}\n'
                           f'[Quote sell] before order balance : [{settlementCurrency_balance}] | {settlementCurrency}')
                # print(f'[Quote sell] before order balance : [{tradedCurrency_balance}] | {tradedCurrency}\n'
                #       f'[Quote sell] before order balance : [{settlementCurrency_balance}] | {settlementCurrency}')
            logger.log('<===== brokerage_balance_order_before_check end =====>')
            # print('<===== brokerage_balance_order_before_check end =====>')
            return {'side': side,
                    'tradedCurrency': tradedCurrency,
                    'settlementCurrency': settlementCurrency,
                    'tradedCurrencyAmount': tradedCurrencyAmount,
                    'quotedSettlementCurrencyAmount': quotedSettlementCurrencyAmount,
                    'tradedCurrency_balance': tradedCurrency_balance,
                    'settlementCurrency_balance': settlementCurrency_balance,
                    'executedPrice': executedPrice}
        else:
            logger('Ask quote failed', 'warning')
    except Exception as ex:
        logger.log(f'brokerage_balance_order_before_check Unknow Error：{str(ex)}', 'critical')
        raise ex


@allure.step("brokerage_balance_order_after_check")
def brokerage_balance_order_after_check(res, balance_before_dict):
    '''
    交易前余额和交易后余额断言，字典格式
    :param res: execute返回结果
    :param balance_before_dict: 涉及的currency币种
    :return:
    '''
    logger.log('<===== brokerage_balance_order_after_check start =====>')
    try:
        side, tradedCurrency, settlementCurrency, tradedCurrencyAmount, quotedSettlementCurrencyAmount, tradedCurrency_before_balance, settlementCurrency_before_balance, executedPrice = \
            balance_before_dict['side'], balance_before_dict['tradedCurrency'], balance_before_dict[
                'settlementCurrency'], \
                balance_before_dict['tradedCurrencyAmount'], balance_before_dict['quotedSettlementCurrencyAmount'], \
                balance_before_dict['tradedCurrency_balance'], balance_before_dict['settlementCurrency_balance'], \
                balance_before_dict['executedPrice']
        res = res['res']['tradeResponse']
        assert side == res[
            'buyTradedCurrency'], f'Quote res side {side} did not match Execute res side {res["buyTradedCurrency"]}'
        assert tradedCurrency == res[
            'tradedCurrency'], f'Quote res tradedCurrency {tradedCurrency} did not match Execute res tradedCurrency {res["tradedCurrency"]}'
        assert settlementCurrency == res[
            'settlementCurrency'], f'Quote res settlementCurrency {settlementCurrency} did not match Execute res settlementCurrency {res["settlementCurrency"]}'
        assert tradedCurrencyAmount == res[
            'quotedTradedCurrencyAmount'], f'Quote res tradedCurrencyAmount {tradedCurrencyAmount} did not match Execute res tradedCurrencyAmount {res["quotedTradedCurrencyAmount"]}'
        assert quotedSettlementCurrencyAmount == res[
            'quotedSettlementCurrencyAmount'], f'Quote res quotedSettlementCurrencyAmount {quotedSettlementCurrencyAmount} did not match Execute res quotedSettlementCurrencyAmount {res["quotedSettlementCurrencyAmount"]}'
        assert executedPrice == res[
            'executedPrice'], f'Quote res executedPrice {executedPrice} did not match Execute res executedPrice {res["executedPrice"]}'
        tradedCurrency_after_balance = get_account_information(currency=tradedCurrency, multiple=False)
        settlementCurrency_after_balance = get_account_information(currency=settlementCurrency, multiple=False)
        if side:
            logger.log(f'Check Buy order traceId:[{res["tradeId"]}]')
            assert Decimal(tradedCurrency_before_balance) + Decimal(
                tradedCurrencyAmount) == Decimal(
                tradedCurrency_after_balance), f'[Buy] tradedCurrency_after_balance did not match - {Decimal(tradedCurrency_before_balance)} + {Decimal(tradedCurrencyAmount)} != {Decimal(tradedCurrency_after_balance)}'
            assert Decimal(settlementCurrency_before_balance) - Decimal(
                quotedSettlementCurrencyAmount) == Decimal(
                settlementCurrency_after_balance), f'[Buy] settlementCurrency_before_balance did not match settlementCurrency_after_balance - {Decimal(settlementCurrency_before_balance)} - {Decimal(quotedSettlementCurrencyAmount)} != {Decimal(settlementCurrency_after_balance)}'
        else:
            logger.log(f'Check Sell order traceId:[{res["tradeId"]}]')
            assert Decimal(tradedCurrency_before_balance) - Decimal(
                tradedCurrencyAmount) == Decimal(
                tradedCurrency_after_balance), f'[Sell] tradedCurrency_before_balance did not match tradedCurrency_after_balance - {Decimal(tradedCurrency_before_balance)} - {Decimal(tradedCurrencyAmount)} != {Decimal(tradedCurrency_after_balance)}'
            assert Decimal(settlementCurrency_before_balance) + Decimal(
                quotedSettlementCurrencyAmount) == Decimal(
                settlementCurrency_after_balance), f'[Sell] settlementCurrency_before_balance did not match settlementCurrency_after_balance - {Decimal(settlementCurrency_before_balance)} + {Decimal(quotedSettlementCurrencyAmount)} != {Decimal(settlementCurrency_after_balance)}'
        logger.log('<===== brokerage_balance_order_after_check end =====>')

    except AssertionError as e:
        logger.log(f'brokerage_balance_order_after_check Assertion Error：{str(e)}', 'error')
        raise e
    except Exception as ex:
        logger.log(f'brokerage_balance_order_after_check Unknow Error：{str(ex)}', 'critical')
        raise ex


@allure.step("quote_execute_apiDetail_assert")
def quote_execute_apiDetail_assert(quote_res, execute_res):
    '''
    function for check the quote and execute api details, match the currencies, amount, qty etc. between two api res.
    :param quote_res:
    :param execute_res:
    :return:
    '''
    logger.log('<===== quote_execute_apiDetail_assert start =====>')
    try:
        # quote和execute接口断言
        quote_buyTradedCurrency = quote_res['res']['quoteResponse']['buyTradedCurrency']
        quote_quotedSettlementCurrencyAmount = Decimal(
            quote_res['res']['quoteResponse']['quotedSettlementCurrencyAmount'])
        quote_quotedTradedCurrencyAmount = Decimal(
            quote_res['res']['quoteResponse']['quotedTradedCurrencyAmount'])
        quote_executedPrice = Decimal(quote_res['res']['quoteResponse']['executedPrice'])
        quote_settlementCurrency = quote_res['res']['quoteResponse']['settlementCurrency']
        quote_tradedCurrency = quote_res['res']['quoteResponse']['tradedCurrency']
        quote_quoteId = quote_res['res']['quoteResponse']['quoteId']

        execute_settlementCurrency = execute_res['res']['tradeResponse']['settlementCurrency']
        execute_tradedCurrency = execute_res['res']['tradeResponse']['tradedCurrency']
        execute_quoteId = execute_res['res']['tradeResponse']['quoteId']
        execute_buyTradedCurrency = execute_res['res']['tradeResponse']['buyTradedCurrency']
        execute_quotedSettlementCurrencyAmount = Decimal(
            execute_res['res']['tradeResponse']['quotedSettlementCurrencyAmount'])
        execute_quotedTradedCurrencyAmount = Decimal(
            execute_res['res']['tradeResponse']['quotedTradedCurrencyAmount'])
        execute_executedPrice = Decimal(execute_res['res']['tradeResponse']['executedPrice'])

        assert quote_buyTradedCurrency == execute_buyTradedCurrency, f'{quote_buyTradedCurrency} != {execute_buyTradedCurrency}'
        assert quote_quotedSettlementCurrencyAmount == execute_quotedSettlementCurrencyAmount, f'{quote_quotedSettlementCurrencyAmount} != {execute_quotedSettlementCurrencyAmount}'
        assert quote_quotedTradedCurrencyAmount == execute_quotedTradedCurrencyAmount, f'{quote_quotedTradedCurrencyAmount} != {execute_quotedTradedCurrencyAmount}'
        assert quote_executedPrice == execute_executedPrice, f'{quote_executedPrice} != {execute_executedPrice}'
        assert quote_settlementCurrency == execute_settlementCurrency, f'{quote_settlementCurrency} != {execute_settlementCurrency}'
        assert quote_tradedCurrency == execute_tradedCurrency, f'{quote_tradedCurrency} != {execute_tradedCurrency}'
        assert quote_quoteId == execute_quoteId, f'{quote_quoteId} != {execute_quoteId}'
        logger.log('<===== quote_execute_apiDetail_assert end =====>')

    except AssertionError as e:
        logger.log(f'quote_execute_apiDetail_assert Assertion Error：{str(e)}', 'error')
        raise e
    except Exception as ex:
        logger.log(f'quote_execute_apiDetail_assert Unknow Error：{str(ex)}', 'critical')
        raise ex

@allure.step("check_rfs_trading_status")
def check_rfs_trading_status(status=True):
    try:
        rfs_status = RFS_API(env).status().get('enabled')
        assert rfs_status == status, f'Need {status} but rfs_trading_status get {rfs_status}'
        logger.log(f'check_rfs_trading_status passed, status {rfs_status}')
    except AssertionError as e:
        logger.log(f'check_rfs_trading_status Assertion Error：{str(e)}', 'error')
        raise e
    except Exception as ex:
        logger.log(f'check_rfs_trading_status Unknow Error：{str(ex)}', 'critical')
        raise ex

@allure.step("check_rfs_LP_gateway")
def check_rfs_LP_gateway(status=True):
    # gateway = read_pytest_ini('rfs_gateway', env)
    connected_value = ''
    try:
        rfs_gateway = RFS_API(env).status_venue()
        logger.log(rfs_gateway)
        for value in rfs_gateway:
            if value['venue'] == gateway and check_LP is True:
                connected_value = value['connected']
                if status and status != connected_value:
                    res = RFS_API(env).turn_on_venus(gateway)
                    assert res['success'] is True, f'Need {gateway} is True but {gateway} get {connected_value}, and I turn it on for u'
                elif status is False and status != connected_value:
                    res = RFS_API(env).turn_off_venus(gateway)
                    assert res['success'] is False, f'Need {gateway} is False but {gateway} get {connected_value}, and I turn it off for u'
                else:
                    logger.log(f'check_rfs_LP_gateway {gateway} is {status}')

    except AssertionError as e:
        logger.log(f'check_rfs_LP_gateway Assertion Error：{str(e)}', 'error')
        raise e
    except Exception as ex:
        logger.log(f'check_rfs_LP_gateway Unknow Error：{str(ex)}', 'critical')
        raise ex


@allure.step("check_ccy_pair")
def check_ccy_pair(quote_req):
    siteGroup = read_pytest_ini('account_siteGroup', env)
    tradedCurrency, settlementCurrency = quote_req['quoteRequest']['tradedCurrency'], quote_req['quoteRequest'][
        'settlementCurrency']
    ccyPair = tradedCurrency + '.' + settlementCurrency
    pair_status = ''
    try:
        res_json = RFS_API(env).cc_pair_status()
        for pair in res_json:
            if pair.get('siteGroup') == siteGroup and pair.get('ccyPair') == ccyPair:
                pair_status = pair.get('enabled')
        assert pair_status is True, f'Need {pair_status} is True but {siteGroup} {ccyPair} get {pair_status}'
        logger.log(f'check_ccy_pair passed, siteGroup - {siteGroup}, ccyPair - {ccyPair}, status - {pair_status}')
    except AssertionError as e:
        logger.log(f'check_ccy_pair Assertion Error：{str(e)}', 'error')
        raise e
    except Exception as ex:
        logger.log(f'check_ccy_pair Unknow Error：{str(ex)}', 'critical')
        raise ex


@allure.step("check_user_transaction")
def check_user_transaction(execute_res):
    try:
        tran_res_json = get_transaction_list()
        tran_list = tran_res_json['transactions'][:2]
        logger.log(tran_list)
        logger.log(execute_res)
        assert tran_list[0]['tradeId'] == tran_list[1]['tradeId'], f'Expect two transaction have different tradeId'
        assert execute_res["tradeId"] == tran_list[0]['tradeId'], f'Execute response not match transaction tradeId'
        credit_order = None
        debit_order = None
        for order in tran_list:
            if order["transactionType"] == "TRADE_CREDIT":
                credit_order = order
            elif order["transactionType"] == "TRADE_DEBIT":
                debit_order = order
        assert credit_order is not None, f'{tran_list} miss TRADE_CREDIT transaction'
        assert debit_order is not None, f'{tran_list} miss TRADE_DEBIT transaction'
        assert credit_order['executedPrice'] == debit_order['executedPrice'], f"{credit_order['executedPrice']} != {debit_order['executedPrice']}"
        if execute_res['buyTradedCurrency']:
            assert execute_res['settlementCurrency'] == debit_order['ccy'], f"settlementCurrency not match, execute {execute_res['settlementCurrency']}, transaction debit_order {debit_order['ccy']}"
            assert execute_res['tradedCurrency'] == credit_order['ccy'], f"tradedCurrency not match, execute {execute_res['tradedCurrency']}, transaction credit_order {credit_order['ccy']}"
            assert Decimal(execute_res['quotedSettlementCurrencyAmount']) == -Decimal(str(debit_order['amount'])), f"SettlementCurrencyAmount not match, execute {Decimal(execute_res['quotedSettlementCurrencyAmount'])}, transaction debit_order {-Decimal(str(debit_order['amount']))}"
            assert Decimal(execute_res['quotedTradedCurrencyAmount']) == Decimal(str(credit_order['amount'])), f"TradedCurrencyAmount not match, execute {Decimal(execute_res['quotedTradedCurrencyAmount'])}, transaction credit_order {Decimal(str(credit_order['amount']))}"
        else:
            assert execute_res['tradedCurrency'] == debit_order['ccy'], f"tradedCurrency not match, execute {execute_res['tradedCurrency']}, transaction debit_order {debit_order['ccy']}"
            assert execute_res['settlementCurrency'] == credit_order['ccy'], f"settlementCurrency not match, execute {execute_res['settlementCurrency']}, transaction credit_order {credit_order['ccy']}"
            assert Decimal(execute_res['quotedTradedCurrencyAmount']) == -Decimal(str(debit_order['amount'])), f"TradedCurrencyAmount not match, execute {Decimal(execute_res['quotedTradedCurrencyAmount'])}, transaction debit_order {-Decimal(str(debit_order['amount']))}"
            assert Decimal(execute_res['quotedSettlementCurrencyAmount']) == Decimal(str(credit_order['amount'])), f"SettlementCurrencyAmount not match, execute {Decimal(execute_res['quotedSettlementCurrencyAmount'])}, transaction credit_order {Decimal(str(credit_order['amount']))}"
    except AssertionError as e:
        logger.log(f'check_user_transaction Assertion Error：{str(e)}', 'error')
        raise e
    except Exception as ex:
        logger.log(f'check_user_transaction Unknow Error：{str(ex)}', 'critical')
        raise ex

@allure.step("check_aggregated_position")
def check_aggregated_position_after_trade(ccy, amount, client_id, original_aggregated_balance_dic, change):
    logger.log('<===== check_aggregated_position_after_trade start =====>')
    try:
        original_aggregated_balance_dict = original_aggregated_balance_dic
        if change:
            new_aggregated_balance_dict = RFS_API(env).aggregated_positions()
            for balance in original_aggregated_balance_dict:
                if balance['tradeCcy'] == ccy:
                    balance['residualPosition'] = float(RTD(Decimal(str(balance['residualPosition'])) + Decimal(str(amount))))
                    balance['maxRfsClientTradeId'] = client_id
                    logger.log(f"{balance['maxRfsClientTradeId']}", 'debug')
                    balance['countRfsClientTradeId'] += 1
                    assert original_aggregated_balance_dict == new_aggregated_balance_dict, f"original_aggregated_balance_dict, new_aggregated_balance_dict, change {original_aggregated_balance_dict}, {new_aggregated_balance_dict}, {change}"
        elif change is False:
            new_aggregated_balance_dict = RFS_API(env).aggregated_positions()
            assert original_aggregated_balance_dict == new_aggregated_balance_dict, f"original_aggregated_balance_dict, new_aggregated_balance_dict, change{original_aggregated_balance_dict}, {new_aggregated_balance_dict}, {change}"
        logger.log('<===== check_aggregated_position_after_trade end =====>')
    except AssertionError as e:
        logger.log(f'check_aggregated_position_after_trade Assertion Error：{str(e)}', 'error')
        raise e
    except Exception as ex:
        logger.log(f'check_aggregated_position_after_trade Unknow Error：{str(ex)}', 'critical')
        raise ex


@allure.step("check_RFS_console_transaction")
def check_RFS_console_transaction(quote_res, execute_res, original_aggregated_balance_dic):
    '''
    TODO: Client['DealerUuid','PrimaryDealerUuid','TreasuryUuid','Spread','TreasurySpread','ClientFundingType','ClientReserve','TreasuryReserve','TreasuryFundingType','ExecutedUserUuid']
    TODO: Order['AverageExecutionPrice','TradeFees','TradeFeesCcy','InternalReference']
    TODO: Position['ResidualPosition','ResidualStatus','FinalSettlementPosition','FinalProfitLoss','FinalTradedPosition']
    :param original_aggregated_balance_dic:
    :param quote_req:
    :param quote_res:
    :param execute_res:
    :return:
    '''
    logger.log('<===== check_RFS_console_transaction start =====>')
    try:
        tran_list = RFS_API(env).trades_completed()['data']
        tran = tran_list[0]
        ClientTrade = tran['ClientTrade']
        Order = tran['Order']
        Position = tran['Position']
        logger.log(ClientTrade, 'debug')
        logger.log(Order, 'debug')
        logger.log(Position, 'debug')
        tradeId_list = [ClientTrade['ReferenceId'], Order['ClientOrderId'], Order['ExternalID'], Order['ReferenceId']]
        assert all(item == execute_res['tradeId'] for item in tradeId_list), f'tradeId_list {tradeId_list} not match {execute_res["tradeId"]}'

        assert ClientTrade['ClientTradeExternalOrderId'] == Order['externalOrderId'], f"ClientTrade['ClientTradeExternalOrderId'] == Order['externalOrderId'] {ClientTrade['ClientTradeExternalOrderId']} == {Order['externalOrderId']}"

        assert quote_res['quoteId'] == ClientTrade['QuoteId'], f"quote_res['quoteId'], ClientTrade['QuoteId'] {quote_res['quoteId']}, {ClientTrade['QuoteId']}"

        BuyTradedCurrency_list = [ClientTrade['BuyTradedCurrency'], Order['BuyTradedCurrency'], Position['clientBuyTradedCurrency']]
        assert all(item == execute_res['buyTradedCurrency'] for item in BuyTradedCurrency_list), f'BuyTradedCurrency_list {BuyTradedCurrency_list} not match {execute_res["buyTradedCurrency"]}'

        siteGroup = read_pytest_ini('account_siteGroup', env)
        siteGroup_list = [ClientTrade['ClientTradeRemarks'], Order['SiteGroup'], Position['Remarks']]
        assert all(item == siteGroup for item in siteGroup_list), f'siteGroup_list {siteGroup_list} not match {siteGroup}'

        test_account = read_pytest_ini('test_account', env)
        assert test_account == ClientTrade['Customer'], f"test_account == ClientTrade['Customer'] {test_account}, {ClientTrade['Customer']}"

        test_account_uid = read_pytest_ini('test_uid', env)
        uid_list = [ClientTrade['AccountGrpUuid'], ClientTrade['UserUuid']]
        assert all(item == test_account_uid for item in uid_list), f'uid_list {uid_list} not match {test_account_uid}'

        execute_SettlementCurrency = execute_res['settlementCurrency']
        execute_TradedCurrency = execute_res['tradedCurrency']
        execute_settlement_amount = Decimal(str(execute_res['quotedSettlementCurrencyAmount']))
        execute_traded_amount = Decimal(str(execute_res['quotedTradedCurrencyAmount']))
        logger.log('debug 1', 'debug')
        pair = execute_TradedCurrency + '.' + execute_SettlementCurrency
        pair_list = [Order['CcyPair'], Position['CcyPair']]
        assert all(item == pair for item in pair_list), f'pair_list {pair_list} not match {pair}'

        settlementCurrency_list = [ClientTrade['SettlementCurrency'], Position['SettlementCcy']]
        assert all(item == execute_SettlementCurrency for item in settlementCurrency_list), f'settlementCurrency_list {settlementCurrency_list} not match {execute_SettlementCurrency}'

        tradeCurrency_list = [ClientTrade['TradedCurrency'], Order['TradedCcy'], Position['TradeCcy']]
        assert all(item == execute_TradedCurrency for item in tradeCurrency_list), f'tradeCurrency_list {tradeCurrency_list} not match {execute_TradedCurrency}'

        settle_amount_list = [Decimal(str(ClientTrade['SettlementCurrencyAmount'])), Decimal(str(Position['clientSettlementAmount']))]
        assert all(item == execute_settlement_amount for item in settle_amount_list), f'settle_amount_list {settle_amount_list} not match {execute_settlement_amount}'

        assert Decimal(str(ClientTrade['TradedCurrencyAmount'])) == Decimal(str(abs(Position['TradedPosition']))), f"Decimal(str(ClientTrade['TradedCurrencyAmount'])) == Decimal(str(abs(Position['TradedPosition']))) {Decimal(str(ClientTrade['TradedCurrencyAmount']))} == {Decimal(str(abs(Position['TradedPosition'])))}"
        logger.log('debug 2', 'debug')

        # 交易数据
        final_traded_amount_list = [Decimal(str(ClientTrade['TradedCurrencyAmount'])), Decimal(str(abs(Position['FinalTradedPosition']))), Decimal(str(abs(Position['TradedPosition'])))]
        assert all(item == execute_traded_amount for item in final_traded_amount_list), f'final_traded_amount_list {final_traded_amount_list} not match {execute_traded_amount}'

        # 已对冲的数据
        assert all([Decimal(str(Order['TradedAmount'])) == Decimal(str(Order['ExecutedAmount'])), Decimal(str(Order['TradedAmount'])) == Decimal(str(Position['TradedAmount']))]), f"{Decimal(str(Order['TradedAmount']))}, {Decimal(str(Order['ExecutedAmount']))}, {Decimal(str(Position['TradedAmount']))}"

        assert 'SETTLED' == ClientTrade['Status'], f"{ClientTrade['Status']} did not match SETTLED"

        assert 'RFS' == ClientTrade['TradeType'], f"{ClientTrade['TradeType']} did not match RFS"

        assert "SUCCESS" == Order['HedgeStatus'], f"{Order['HedgeStatus']} did not match SUCCESS"

        assert "SUCCESS" == Order['OrderExecutionStatus'], f"{Order['OrderExecutionStatus']} did not match SUCCESS"

        gateway = read_pytest_ini('rfs_gateway', env)
        venue_list = [Order['Venue'], Position['Venue']]
        # assert all(item == gateway for item in venue_list), f'venue_list {venue_list} not match {gateway}'

        assert "HEDGED" == Position['PositionStatus'], f"{Position['PositionStatus']}"

        assert all([ClientTrade['ClientTradeId'] == Order['ClientTradeId'], ClientTrade['ClientTradeId'] == Position['RfsClientTradeId']]), f"ClientTrade['ClientTradeId'], Order['ClientTradeId'], Position['ClientTradeId'],{ClientTrade['ClientTradeId']}, {Order['ClientTradeId']}, {Position['ClientTradeId']}"
        logger.log('debug 3', 'debug')

        assert all([ClientTrade['PositionId'] == Order['PositionID'], ClientTrade['PositionId'] == Position['PositionID']]), f"ClientTrade['PositionId'], Order['PositionID'], Position['PositionID'],{ClientTrade['PositionId']}, {Order['PositionID']}, {Position['PositionID']}"

        assert ClientTrade['OrderId'] == Order['OrderId'], f"ClientTrade['OrderId'], Order['OrderId'], {ClientTrade['OrderId']}, {Order['OrderId']}"

        assert ClientTrade['synthetic'] == Position['synthetic'], f"ClientTrade['synthetic'] == Position['synthetic']{ClientTrade['synthetic']}, {Position['synthetic']}"

        assert all([ClientTrade['naturalSettlementCcy'] == Order['SettlementCcy'], ClientTrade['naturalSettlementCcy'] == Position['hedgeSettlementCcy']]), f"{ClientTrade['naturalSettlementCcy']}, {Order['SettlementCcy']}, {Position['hedgeSettlementCcy']}"

        assert Order['LimitPrice'] == Position['limitPrice'], f"Order['LimitPrice'] == Position['limitPrice'], {Order['LimitPrice']}, {Position['limitPrice']}"

        assert Order['SettlementAmount'] == Position['SettlementAmount'], f"Order['SettlementAmount'] == Position['SettlementAmount'],{Order['SettlementAmount']}, {Position['SettlementAmount']}"
        # 判断是否是非同币种对冲，若是，则需要计算currency的转换
        if ClientTrade['synthetic']:
            est_mdsRateCurrencyPair = execute_SettlementCurrency + "/" + ClientTrade['naturalSettlementCcy']
            assert est_mdsRateCurrencyPair == ClientTrade['mdsRateCurrencyPair'], f"est_mdsRateCurrencyPair == ClientTrade['mdsRateCurrencyPair'], {est_mdsRateCurrencyPair}, {ClientTrade['mdsRateCurrencyPair']}"

            assert ClientTrade['mdsRateCurrencyBid'] == Position['mdsRateCurrencyBid'], f"ClientTrade['mdsRateCurrencyBid'] == Position['mdsRateCurrencyBid'], {ClientTrade['mdsRateCurrencyBid']}, {Position['mdsRateCurrencyBid']}"

            assert ClientTrade['mdsRateCurrencyOffer'] == Position['mdsRateCurrencyOffer'], f"ClientTrade['mdsRateCurrencyOffer'] == Position['mdsRateCurrencyOffer'], {ClientTrade['mdsRateCurrencyOffer']}, {Position['mdsRateCurrencyOffer']}"

            # 对冲aggregation position
            if Position['ResidualStatus'] == "PENDING_AGGREGATION":
                check_aggregated_position_after_trade(Position['TradeCcy'], Position['ResidualPosition'], ClientTrade['ClientTradeId'], original_aggregated_balance_dic, change=True)
                logger.log("PENDING_AGGREGATION case")
            elif Position['ResidualStatus'] == 'NA':
                check_aggregated_position_after_trade(Position['TradeCcy'], Position['ResidualPosition'], ClientTrade['ClientTradeId'], original_aggregated_balance_dic, change=False)
                logger.log("Not aggregation")

            # synthetic的买单
            if ClientTrade['BuyTradedCurrency']:

                P_SettlementPosition = RTD(Decimal(str(Position['mdsRateCurrencyOffer'])) * Decimal(str(Position['clientSettlementAmount'])))
                assert P_SettlementPosition == Decimal(str(Position['SettlementPosition'])), f"[buy] P_SettlementPosition = round_to_decimal(Decimal(str(Position['mdsRateCurrencyOffer'])) * Decimal(str(Position['clientSettlementAmount']))), {Decimal(str(Position['SettlementPosition']))}, {P_SettlementPosition}, {Decimal(str(Position['mdsRateCurrencyOffer']))} * {Decimal(str(Position['clientSettlementAmount']))}"

                logger.log('1','debug')
                P_SettlementAmount = RTD(Decimal(str(Position['TradedAmount'])) * Decimal(str(Position['limitPrice'])))
                assert P_SettlementAmount == Decimal(str(Position['SettlementAmount'])), f"[buy] P_SettlementAmount == Decimal(str(Position['SettlementAmount'])), {P_SettlementAmount}, {Decimal(str(Position['SettlementAmount']))}, {Decimal(str(Position['TradedAmount']))} * {Decimal(str(Position['limitPrice']))}"

                logger.log('2','debug')
                P_SettlementPosition = RTD(Decimal(str(Position['SettlementAmount'])) + Decimal(str(Position['FinalProfitLoss'])))
                assert P_SettlementPosition == Decimal(str(Position['SettlementPosition'])), f"P_SettlementPosition = round_to_decimal(Decimal(str(Position['SettlementAmount'])) + Decimal(str(Position['FinalProfitLoss']))), {P_SettlementPosition}, {Decimal(str(Position['SettlementAmount']))} + {Decimal(str(Position['FinalProfitLoss']))}"

                P_FinalProfitLoss = RTD(Decimal(str(Position['FinalSettlementPosition'])) - Decimal(str(Position['SettlementAmount'])))
                assert P_FinalProfitLoss == Decimal(str(Position['FinalProfitLoss'])), f"P_FinalProfitLoss == Decimal(str(Position['FinalProfitLoss'])), {P_FinalProfitLoss}, {Decimal(str(Position['FinalSettlementPosition']))} - {Decimal(str(Position['SettlementAmount']))}"

                assert execute_traded_amount == -Decimal(str(Position['FinalTradedPosition'])), f"execute_traded_amount == -Decimal(str(Position['FinalTradedPosition'])), {execute_traded_amount}, {-Decimal(str(Position['FinalTradedPosition']))}"

                assert execute_settlement_amount == Decimal(str(Position['clientSettlementAmount'])), f"execute_settlement_amount == -Decimal(str(Position['TradedPosition'])), {execute_settlement_amount}, {Decimal(str(Position['clientSettlementAmount']))}"

                # 可能存在未对冲的数据
                assert execute_traded_amount == RTD(Decimal(str(Order['TradedAmount'])) - Decimal(str(Position['ResidualPosition']))), f"execute_traded_amount == round_to_decimal(-Decimal(str(Order['TradedAmount'])) + Decimal(str(Position['ResidualPosition']))), {execute_traded_amount}, {Decimal(str(Order['TradedAmount']))}, {Decimal(str(Position['ResidualPosition']))}"

            # synthetic的卖单
            elif ClientTrade['BuyTradedCurrency'] is False:

                P_SettlementPosition = -RTD(Decimal(str(Position['mdsRateCurrencyBid'])) * Decimal(str(Position['clientSettlementAmount'])))
                assert P_SettlementPosition == Decimal(str(Position['SettlementPosition'])), f"[sell] P_SettlementPosition = -round_to_decimal(Decimal(str(Position['mdsRateCurrencyBid'])) * Decimal(str(Position['clientSettlementAmount']))), {Decimal(str(Position['SettlementPosition']))}, {P_SettlementPosition}, {-Decimal(str(Position['mdsRateCurrencyBid']))} * {Decimal(str(Position['clientSettlementAmount']))}"

                P_SettlementAmount = RTD(Decimal(str(Position['TradedAmount'])) * Decimal(str(Position['limitPrice'])))
                assert P_SettlementAmount == Decimal(str(Position['SettlementAmount'])), f"[sell] P_SettlementAmount = round_to_decimal(Decimal(str(Position['TradedAmount'])) * Decimal(str(Position['limitPrice']))), {Decimal(str(Position['SettlementAmount']))}, {P_SettlementAmount}, {Decimal(str(Position['TradedAmount']))} * {Decimal(str(Position['limitPrice']))}"

                P_SettlementPosition = RTD(-Decimal(str(Position['SettlementAmount'])) + Decimal(str(Position['FinalProfitLoss'])))
                assert P_SettlementPosition == Decimal(str(Position['SettlementPosition'])), f"P_SettlementPosition == Position['SettlementPosition'], {P_SettlementPosition}, {Position['SettlementPosition']}"

                P_FinalProfitLoss = RTD(Decimal(str(Position['FinalSettlementPosition'])) + Decimal(str(Position['SettlementAmount'])))
                assert P_FinalProfitLoss == Decimal(str(Position['FinalProfitLoss'])), f" P_FinalProfitLoss == Decimal(str(Position['FinalProfitLoss'])), {P_FinalProfitLoss}, {Decimal(str(Position['FinalSettlementPosition']))} + {Decimal(str(Position['SettlementAmount']))}"

                assert execute_traded_amount == Decimal(str(Position['FinalTradedPosition'])), f"execute_traded_amount == Decimal(str(Position['FinalTradedPosition'])), {execute_traded_amount}, {Decimal(str(Position['FinalTradedPosition']))}"

                assert execute_settlement_amount == Decimal(str(Position['clientSettlementAmount'])), f"execute_settlement_amount == Decimal(str(Position['TradedPosition'])), {execute_settlement_amount}, {Decimal(str(Position['clientSettlementAmount']))}"

                # 可能存在未对冲的数据
                assert execute_traded_amount == RTD(Decimal(str(Order['TradedAmount'])) + Decimal(str(Position['ResidualPosition']))), f"execute_traded_amount == round_to_decimal(Decimal(str(Order['TradedAmount'])) + Decimal(str(Position['ResidualPosition']))), {execute_traded_amount}, {Decimal(str(Order['TradedAmount']))}, {Decimal(str(Position['ResidualPosition']))}"

        elif ClientTrade['synthetic'] is False:
            assert '' == ClientTrade['mdsRateCurrencyPair'], f"'' == ClientTrade['mdsRateCurrencyPair'], {ClientTrade['mdsRateCurrencyPair']} should be empty"

            mdsRateCurrency_list = [Position['mdsRateCurrencyBid'], Position['mdsRateCurrencyBid'], ClientTrade['mdsRateCurrencyOffer'], Position['mdsRateCurrencyOffer']]
            assert all(item == 0 for item in mdsRateCurrency_list), f'mdsRateCurrency_list {mdsRateCurrency_list} should all be 0'

            # 对冲aggregation position
            if Position['ResidualStatus'] == "PENDING_AGGREGATION":
                check_aggregated_position_after_trade(Position['TradeCcy'], Position['ResidualPosition'], ClientTrade['ClientTradeId'], original_aggregated_balance_dic, change=True)
                logger.log("PENDING_AGGREGATION case")
            elif Position['ResidualStatus'] == 'NA':
                check_aggregated_position_after_trade(Position['TradeCcy'], Position['ResidualPosition'], ClientTrade['ClientTradeId'], original_aggregated_balance_dic, change=False)
                logger.log("Not aggregation")

            if ClientTrade['BuyTradedCurrency']:
                P_SettlementPosition = Decimal(str(Position['clientSettlementAmount']))
                assert P_SettlementPosition == Decimal(str(Position['SettlementPosition'])), f"P_SettlementPosition == Decimal(str(Position['SettlementPosition'])), {P_SettlementPosition}, {Decimal(str(Position['clientSettlementAmount']))}"

                P_SettlementAmount = RTD(Decimal(str(Position['TradedAmount'])) * Decimal(str(Position['limitPrice'])))
                assert P_SettlementAmount == Decimal(str(Position['SettlementAmount'])), f"P_SettlementAmount == Decimal(str(Position['SettlementAmount'])), {P_SettlementAmount}, {Decimal(str(Position['SettlementAmount']))}, {Decimal(str(Position['TradedAmount']))} * {Decimal(str(Position['limitPrice']))}"

                P_SettlementPosition = RTD(Decimal(str(Position['SettlementAmount'])) + Decimal(str(Position['FinalProfitLoss'])))
                assert P_SettlementPosition == Decimal(str(Position['SettlementPosition'])), f"P_SettlementPosition == Position['SettlementPosition'], {P_SettlementPosition}, {Decimal(str(Position['SettlementAmount']))} + {Decimal(str(Position['FinalProfitLoss']))}"

                P_FinalProfitLoss = RTD(Decimal(str(Position['FinalSettlementPosition'])) - Decimal(str(Position['SettlementAmount'])))
                assert P_FinalProfitLoss == Decimal(str(Position['FinalProfitLoss'])), f"P_FinalProfitLoss == Decimal(str(Position['FinalProfitLoss'])), {P_FinalProfitLoss}, {Decimal(str(Position['FinalSettlementPosition']))} - {Decimal(str(Position['SettlementAmount']))}"

                assert execute_traded_amount == -Decimal(str(Position['FinalTradedPosition'])), f"execute_traded_amount == -Decimal(str(Position['FinalTradedPosition'])), {execute_traded_amount}, {-Decimal(str(Position['FinalTradedPosition']))}"

                assert execute_settlement_amount == Decimal(str(Position['clientSettlementAmount'])), f"execute_settlement_amount == -Decimal(str(Position['TradedPosition'])), {execute_settlement_amount}, {Decimal(str(Position['clientSettlementAmount']))}"

                # 可能存在未对冲的数据
                assert execute_traded_amount == RTD(Decimal(str(Order['TradedAmount'])) + Decimal(str(Position['ResidualPosition']))), f"[synthetic false] execute_traded_amount == round_to_decimal(-Decimal(str(Order['TradedAmount'])) + Decimal(str(Position['ResidualPosition']))), {execute_traded_amount}, {Decimal(str(Order['TradedAmount']))}, {Decimal(str(Position['ResidualPosition']))}"

            elif ClientTrade['BuyTradedCurrency'] is False:
                P_SettlementPosition = -Decimal(str(Position['clientSettlementAmount']))
                assert P_SettlementPosition == Decimal(str(Position['SettlementPosition'])), f"P_SettlementPosition == Decimal(str(Position['SettlementPosition'])), {P_SettlementPosition}, {Decimal(str(Position['clientSettlementAmount']))}"

                P_SettlementAmount = RTD(Decimal(str(Position['TradedAmount'])) * Decimal(str(Position['limitPrice'])))
                assert P_SettlementAmount == Decimal(str(Position['SettlementAmount'])), f"P_SettlementAmount == Decimal(str(Position['SettlementAmount'])), {P_SettlementAmount}, {Decimal(str(Position['SettlementAmount']))}, {Decimal(str(Position['TradedAmount']))} * {Decimal(str(Position['limitPrice']))}"

                P_SettlementPosition = RTD(-Decimal(str(Position['SettlementAmount'])) + Decimal(str(Position['FinalProfitLoss'])))
                assert P_SettlementPosition == Decimal(str(Position['SettlementPosition'])), f"P_SettlementPosition == Position['SettlementPosition'], {P_SettlementPosition}, {Position['SettlementPosition']}"

                P_FinalProfitLoss = RTD(Decimal(str(Position['FinalSettlementPosition'])) + Decimal(str(Position['SettlementAmount'])))
                assert P_FinalProfitLoss == Decimal(str(Position['FinalProfitLoss'])), f"P_FinalProfitLoss == Decimal(str(Position['FinalProfitLoss'])), {P_FinalProfitLoss}, {Decimal(str(Position['FinalSettlementPosition']))} + {Decimal(str(Position['SettlementAmount']))}"

                assert execute_traded_amount == Decimal(str(Position['FinalTradedPosition'])), f"execute_traded_amount == Decimal(str(Position['FinalTradedPosition'])), {execute_traded_amount}, {Decimal(str(Position['FinalTradedPosition']))}"

                assert execute_settlement_amount == Decimal(str(Position['clientSettlementAmount'])), f"execute_settlement_amount == Decimal(str(Position['TradedPosition'])), {execute_settlement_amount}, {Decimal(str(Position['clientSettlementAmount']))}"

                # 可能存在未对冲的数据
                assert execute_traded_amount == RTD(Decimal(str(Order['TradedAmount'])) + Decimal(str(Position['ResidualPosition']))), f"execute_traded_amount == round_to_decimal(Decimal(str(Order['TradedAmount'])) + Decimal(str(Position['ResidualPosition']))), {execute_traded_amount}, {Decimal(str(Order['TradedAmount']))}, {Decimal(str(Position['ResidualPosition']))}"
        logger.log('<===== check_RFS_console_transaction end =====>')
        rate = ''
        logger.log(f"ClientTrade['BuyTradedCurrency'] {ClientTrade['BuyTradedCurrency']}", 'debug')
        if ClientTrade['BuyTradedCurrency']:
            logger.log(f"true ClientTrade['BuyTradedCurrency'] {ClientTrade['BuyTradedCurrency']}", 'debug')
            rate = Position['mdsRateCurrencyOffer']
            logger.log(f"rate {rate}")
        elif ClientTrade['BuyTradedCurrency'] is False:
            logger.log(f"false ClientTrade['BuyTradedCurrency'] {ClientTrade['BuyTradedCurrency']}", 'debug')
            rate = Position['mdsRateCurrencyBid']
            logger.log(f"rate {rate}")
        return Position['SettlementAmount'], Position['TradedAmount'], rate

    except AssertionError as e:
        logger.log(f'check_RFS_console_transaction Assertion Error：{str(e)}', 'error')
        raise e
    except Exception as ex:
        logger.log(f'check_RFS_console_transaction Unknow Error：{str(ex)}', 'critical')
        raise ex


@allure.step('assertion_with_ops_transaction_for_RFQ')
def assertion_ops_transaction_RFQ(traceId, execute_res, hedge_settlement_amount, hedge_trade_amount, rate):
    logger.log('<===== assertion_ops_transaction_RFQ start =====>')
    platformTrade_Float_amount = RTD((hedge_settlement_amount * rate) / (1 - 0.0001 - 0.01) * (1 - 0.01))
    logger.log(f'hedge_settlement_amount {hedge_settlement_amount}, rate {rate}', 'debug')
    logger.log(f'platformTrade_Float_amount {platformTrade_Float_amount}', 'debug')
    try:
        ops_tran_data = OPS_API(env).ops_transaction(traceId)
        test_account = read_pytest_ini('test_account', env)
        # 创建一个 defaultdict 来分类数据
        classified_data = defaultdict(list)

        # 遍历原始数据并按 transactionClass 进行分类
        for item in ops_tran_data:
            transaction_class = item['transactionClass']
            classified_data[transaction_class].append(item)

        # 将 defaultdict 转换为普通字典
        classified_data = dict(classified_data)
        logger.log(f"classified_data: {classified_data}",'debug')
        # 确保有四个key
        assert len(classified_data) == 4, f'RFQ transactionClass should have 4 but got {len(classified_data)}'
        transaction_class_list = ['altcoinx.RfsOffPlatformTradeTransaction', 'altcoinx.RfsFloatTransaction', 'altcoinx.RfsHedgedOffPlatformTradeTransaction', 'altcoinx.RfsTradeTransaction']
        for key, values in classified_data.items():
            assert key in transaction_class_list, f'{key} is not belong to RFQ transactions'
            # 确保有各有四条transaction
            assert len(values) == 4, f'{key} class should have 4 transaction but got {len(classified_data)}'

        transaction_assert_count = 0
        for value in classified_data['altcoinx.RfsOffPlatformTradeTransaction']:
            if execute_res['buyTradedCurrency']:
                if value['account']['owner']['username'] == 'christine.sze+offplatform.oslsg@osl.com':
                    if value['ccy'] == 'USD':
                        assert value['transactionType'] == 'TRADE_CREDIT', f"RfsOffPlatformTradeTransaction buy value['transactionType'] == 'TRADE_CREDIT',{value['transactionType']}, TRADE_CREDIT"
                        # assert value['amount'] == platformTrade_Float_amount, f"RfsOffPlatformTradeTransaction buy {value['amount']} == {platformTrade_Float_amount}"
                        transaction_assert_count += 1
                    elif value['ccy'] == execute_res['tradedCurrency']:
                        assert value['transactionType'] == 'TRADE_DEBIT', f"RfsOffPlatformTradeTransaction buy assert value['transactionType'] == 'TRADE_DEBIT', {value['transactionType']}, TRADE_DEBIT"
                        assert Decimal(str(value['amount'])) == Decimal(str(execute_res['quotedTradedCurrencyAmount'])), f"RfsOffPlatformTradeTransaction buy {Decimal(str(value['amount']))} == {Decimal(str(execute_res['quotedTradedCurrencyAmount']))}"
                        transaction_assert_count += 1

                    else:
                        logger.log(
                            '[buy] RfsOffPlatformTradeTransaction AssertionError : christine.sze+offplatform.oslsg@osl.com')
                elif value['account']['owner']['username'] == 'prakash.konagi+dealer_ds@osl.com':
                    if value['ccy'] == 'USD':
                        assert value['transactionType'] == 'TRADE_DEBIT', f"RfsOffPlatformTradeTransaction buy assert value['transactionType'] == 'TRADE_DEBIT', {value['transactionType']}, TRADE_DEBIT"
                        # assert value['amount'] == platformTrade_Float_amount, f"RfsOffPlatformTradeTransaction buy {value['amount']} == {platformTrade_Float_amount}"
                        transaction_assert_count += 1

                    elif value['ccy'] == execute_res['tradedCurrency']:
                        assert value['transactionType'] == 'TRADE_CREDIT', f"RfsOffPlatformTradeTransaction buy assert value['transactionType'] == 'TRADE_CREDIT', {value['transactionType']}, TRADE_CREDIT"
                        assert Decimal(str(value['amount'])) == Decimal(str(execute_res['quotedTradedCurrencyAmount'])), f"RfsOffPlatformTradeTransaction buy {Decimal(str(value['amount']))} == {Decimal(str(execute_res['quotedTradedCurrencyAmount']))}"
                        transaction_assert_count += 1

                    else:
                        logger.log(
                            '[buy] RfsOffPlatformTradeTransaction AssertionError : prakash.konagi+dealer_ds@osl.com')
            elif execute_res['buyTradedCurrency'] is False:
                if value['account']['owner']['username'] == 'christine.sze+offplatform.oslsg@osl.com':
                    if value['ccy'] == 'USD':
                        assert value['transactionType'] == 'TRADE_DEBIT', f"RfsOffPlatformTradeTransaction sell transactionType assert value['transactionType'] == 'TRADE_DEBIT', {value['transactionType']}, TRADE_DEBIT"
                        # assert value['amount'] == platformTrade_Float_amount, f"RfsOffPlatformTradeTransaction sell {value['amount']} == {platformTrade_Float_amount}"
                        transaction_assert_count += 1

                    elif value['ccy'] == execute_res['tradedCurrency']:
                        assert value['transactionType'] == 'TRADE_CREDIT', f"RfsOffPlatformTradeTransaction sell transactionType assert value['transactionType'] == 'TRADE_CREDIT', {value['transactionType']}, TRADE_CREDIT"
                        assert Decimal(str(value['amount'])) == Decimal(str(execute_res['quotedTradedCurrencyAmount'])), f"RfsOffPlatformTradeTransaction sell {Decimal(str(value['amount']))} == {Decimal(str(execute_res['quotedTradedCurrencyAmount']))}"
                        transaction_assert_count += 1

                    else:
                        logger.log(
                            '[sell] RfsOffPlatformTradeTransaction AssertionError : christine.sze+offplatform.oslsg@osl.com')
                elif value['account']['owner']['username'] == 'prakash.konagi+dealer_ds@osl.com':
                    if value['ccy'] == 'USD':
                        assert value['transactionType'] == 'TRADE_CREDIT', f"RfsOffPlatformTradeTransaction sell transactionType assert value['transactionType'] == 'TRADE_CREDIT', {value['transactionType']}, TRADE_CREDIT"
                        # assert value['amount'] == platformTrade_Float_amount, f"RfsOffPlatformTradeTransaction sell {value['amount']} == {platformTrade_Float_amount}"
                        transaction_assert_count += 1

                    elif value['ccy'] == execute_res['tradedCurrency']:
                        assert value['transactionType'] == 'TRADE_DEBIT', f"RfsOffPlatformTradeTransaction sell transactionType assert value['transactionType'] == 'TRADE_DEBIT', {value['transactionType']}, TRADE_DEBIT"
                        assert Decimal(str(value['amount'])) == Decimal(str(execute_res['quotedTradedCurrencyAmount'])), f"RfsOffPlatformTradeTransaction sell {Decimal(str(value['amount']))} == {Decimal(str(execute_res['quotedTradedCurrencyAmount']))}"
                        transaction_assert_count += 1

                    else:
                        logger.log(
                            '[sell] RfsOffPlatformTradeTransaction AssertionError : prakash.konagi+dealer_ds@osl.com')

        for value in classified_data['altcoinx.RfsTradeTransaction']:
            if execute_res['buyTradedCurrency']:
                if value['account']['owner']['username'] == test_account:
                    if value['ccy'] == execute_res['settlementCurrency']:
                        assert value['transactionType'] == 'TRADE_DEBIT', f"buy assert value['transactionType'] == 'TRADE_DEBIT', {value['transactionType']}, TRADE_DEBIT"
                        assert Decimal(str(value['amount'])) == Decimal(execute_res['quotedSettlementCurrencyAmount']), f"RfsTradeTransaction buy assert Decimal(str(value['amount'])) == Decimal(execute_res['quotedSettlementCurrencyAmount']), {Decimal(str(value['amount']))} == {Decimal(execute_res['quotedSettlementCurrencyAmount'])}"
                        transaction_assert_count += 1

                    elif value['ccy'] == execute_res['tradedCurrency']:
                        assert value['transactionType'] == 'TRADE_CREDIT', f"buy assert value['transactionType'] == 'TRADE_CREDIT', {value['transactionType']}, TRADE_CREDIT"
                        assert Decimal(str(value['amount'])) == Decimal(execute_res['quotedTradedCurrencyAmount']), f"RfsTradeTransaction buy assert Decimal(str(value['amount'])) == Decimal(execute_res['quotedTradedCurrencyAmount']), {Decimal(value['amount'])} == {Decimal(execute_res['quotedTradedCurrencyAmount'])}"
                        transaction_assert_count += 1

                    else:
                        logger.log(f'[buy] RfsTradeTransaction AssertionError : {test_account}')

                elif value['account']['owner']['username'] == 'prakash.konagi+dealer_ds@osl.com':
                    if value['ccy'] == execute_res['settlementCurrency']:
                        assert value['transactionType'] == 'TRADE_CREDIT', f"buy assert value['transactionType'] == 'TRADE_CREDIT', {value['transactionType']}, TRADE_CREDIT"
                        assert Decimal(str(value['amount'])) == Decimal(execute_res['quotedSettlementCurrencyAmount']), f"RfsTradeTransaction buy assert str(value['amount']) == execute_res['quotedSettlementCurrencyAmount'], {value['amount']} == {execute_res['quotedSettlementCurrencyAmount']}"
                        transaction_assert_count += 1


                    elif value['ccy'] == execute_res['tradedCurrency']:
                        assert value['transactionType'] == 'TRADE_DEBIT', f"buy assert value['transactionType'] == 'TRADE_DEBIT', {value['transactionType']}, TRADE_DEBIT"
                        assert Decimal(str(value['amount'])) == Decimal(execute_res['quotedTradedCurrencyAmount']), f"RfsTradeTransaction buy assert str(value['amount']) == execute_res['quotedTradedCurrencyAmount'], {value['amount']} == {execute_res['quotedTradedCurrencyAmount']}"
                        transaction_assert_count += 1

                    else:
                        logger.log(f'[buy] RfsTradeTransaction AssertionError : prakash.konagi+dealer_ds@osl.com')

            elif execute_res['buyTradedCurrency'] is False:
                if value['account']['owner']['username'] == test_account:
                    if value['ccy'] == execute_res['settlementCurrency']:
                        assert value['transactionType'] == 'TRADE_CREDIT', f"sell assert value['transactionType'] == 'TRADE_CREDIT', {value['transactionType']}, TRADE_CREDIT"
                        assert Decimal(str(value['amount'])) == Decimal(execute_res['quotedSettlementCurrencyAmount']), f"RfsTradeTransaction sell assert Decimal(str(value['amount'])) == execute_res['quotedSettlementCurrencyAmount'], {value['amount']} == {execute_res['quotedSettlementCurrencyAmount']}"
                        transaction_assert_count += 1
                    elif value['ccy'] == execute_res['tradedCurrency']:
                        assert value['transactionType'] == 'TRADE_DEBIT', f"sell assert value['transactionType'] == 'TRADE_DEBIT', {value['transactionType']}, TRADE_DEBIT"
                        assert Decimal(str(value['amount'])) == Decimal(execute_res['quotedTradedCurrencyAmount']), f"RfsTradeTransaction sell assert Decimal(str(value['amount'])) == execute_res['quotedTradedCurrencyAmount'], {value['amount']} == {execute_res['quotedTradedCurrencyAmount']}"
                        transaction_assert_count += 1

                    else:
                        logger.log(f'[sell] RfsTradeTransaction AssertionError : {test_account}')
                elif value['account']['owner']['username'] == 'prakash.konagi+dealer_ds@osl.com':
                    if value['ccy'] == execute_res['settlementCurrency']:
                        assert value['transactionType'] == 'TRADE_DEBIT', f"RfsTradeTransaction sell assert value['transactionType'] == 'TRADE_DEBIT', {value['transactionType']}, TRADE_DEBIT"
                        assert Decimal(str(value['amount'])) == Decimal(execute_res[
                            'quotedSettlementCurrencyAmount']), f"RfsTradeTransaction sell assert Decimal(str(value['amount'])) == execute_res['quotedSettlementCurrencyAmount'],{value['amount']} == {execute_res['quotedSettlementCurrencyAmount']}"
                        transaction_assert_count += 1
                    elif value['ccy'] == execute_res['tradedCurrency']:
                        assert value['transactionType'] == 'TRADE_CREDIT', f"sell assert value['transactionType'] == 'TRADE_CREDIT', {value['transactionType']}, TRADE_CREDIT"
                        assert Decimal(str(value['amount'])) == Decimal(execute_res['quotedTradedCurrencyAmount']), f"RfsTradeTransaction sell assert Decimal(str(value['amount'])) == execute_res['quotedTradedCurrencyAmount'], {value['amount']} == {execute_res['quotedTradedCurrencyAmount']}"
                        transaction_assert_count += 1
                    else:
                        logger.log(f'[sell] RfsTradeTransaction AssertionError : prakash.konagi+dealer_ds@osl.com')

        for value in classified_data['altcoinx.RfsHedgedOffPlatformTradeTransaction']:
            if execute_res['buyTradedCurrency']:
                if value['account']['owner']['username'] == 'billy.chan+ethdealer@osl.com':
                    if value['ccy'] == 'USD':
                        assert value['transactionType'] == 'TRADE_DEBIT', f"RfsHedgedOffPlatformTradeTransaction buy assert value['transactionType'] == 'TRADE_DEBIT', {value['transactionType']}, TRADE_DEBIT"
                        assert value['amount'] == hedge_settlement_amount, f"RfsHedgedOffPlatformTradeTransaction buy assert value['amount'] == hedge_amount, {value['amount']} == {hedge_settlement_amount}"
                        transaction_assert_count += 1

                    elif value['ccy'] == execute_res['tradedCurrency']:
                        assert value['transactionType'] == 'TRADE_CREDIT', f"RfsHedgedOffPlatformTradeTransaction buy assert value['transactionType'] == 'TRADE_CREDIT', {value['transactionType']}, TRADE_CREDIT"
                        assert Decimal(str(value['amount'])) == Decimal(execute_res['quotedTradedCurrencyAmount']), f"RfsHedgedOffPlatformTradeTransaction buy assert Decimal(str(value['amount'])) == execute_res['quotedTradedCurrencyAmount'], {value['amount']} == {execute_res['quotedTradedCurrencyAmount']}"
                        transaction_assert_count += 1

                    else:
                        logger.log(
                            f'[buy] RfsHedgedOffPlatformTradeTransaction AssertionError : billy.chan+ethdealer@osl.com')

                elif value['account']['owner']['username'] == 'christine.sze+oslsgexc@bc.group':
                    if value['ccy'] == "USD":
                        assert value['transactionType'] == 'TRADE_CREDIT', f"buy assert value['transactionType'] == 'TRADE_CREDIT', {value['transactionType']}, TRADE_CREDIT"
                        assert value['amount'] == hedge_settlement_amount, f"RfsHedgedOffPlatformTradeTransaction buy assert value['amount'] == hedge_amount, {value['amount']} == {hedge_settlement_amount}"
                        transaction_assert_count += 1

                    elif value['ccy'] == execute_res['tradedCurrency']:
                        assert value['transactionType'] == 'TRADE_DEBIT', f"RfsHedgedOffPlatformTradeTransaction buy assert value['transactionType'] == 'TRADE_DEBIT', {value['transactionType']}, TRADE_DEBIT"
                        assert Decimal(str(value['amount'])) == Decimal(execute_res['quotedTradedCurrencyAmount']), f"RfsHedgedOffPlatformTradeTransaction buy assert Decimal(str(value['amount'])) == execute_res['quotedTradedCurrencyAmount'], {value['amount']} == {execute_res['quotedTradedCurrencyAmount']}"
                        transaction_assert_count += 1

                    else:
                        logger.log(
                            f'[buy] RfsHedgedOffPlatformTradeTransaction AssertionError : christine.sze+oslsgexc@bc.group')
            elif execute_res['buyTradedCurrency'] is False:
                if value['account']['owner']['username'] == 'billy.chan+ethdealer@osl.com':
                    if value['ccy'] == 'USD':
                        assert value['transactionType'] == 'TRADE_CREDIT', f"RfsHedgedOffPlatformTradeTransaction sell assert value['transactionType'] == 'TRADE_CREDIT', {value['transactionType']}, TRADE_CREDIT"
                        assert value['amount'] == hedge_settlement_amount, f"RfsHedgedOffPlatformTradeTransaction sell assert value['amount'] == hedge_amount, {value['amount']} == hedge_amount"
                        transaction_assert_count += 1
                    elif value['ccy'] == execute_res['tradedCurrency']:
                        assert value['transactionType'] == 'TRADE_DEBIT', f"RfsHedgedOffPlatformTradeTransaction sell assert value['transactionType'] == 'TRADE_DEBIT', {value['transactionType']}, TRADE_DEBIT"
                        assert Decimal(str(value['amount'])) == Decimal(str(hedge_trade_amount)), f"RfsHedgedOffPlatformTradeTransaction sell assert Decimal(str(value['amount'])) == execute_res['quotedTradedCurrencyAmount'], {Decimal(str(value['amount']))} == {Decimal(str(hedge_trade_amount))}"
                        transaction_assert_count += 1
                    else:
                        logger.log(
                            f'[sell] RfsHedgedOffPlatformTradeTransaction AssertionError : billy.chan+ethdealer@osl.com')
                elif value['account']['owner']['username'] == 'christine.sze+oslsgexc@bc.group':
                    if value['ccy'] == 'USD':
                        assert value['transactionType'] == 'TRADE_DEBIT', f"RfsHedgedOffPlatformTradeTransaction sell assert value['transactionType'] == 'TRADE_DEBIT', {value['transactionType']}, TRADE_DEBIT"
                        assert value['amount'] == hedge_settlement_amount, f"RfsHedgedOffPlatformTradeTransaction sell assert value['amount'] == hedge_amount, {value['amount']} == {round(hedge_settlement_amount, 2)}"
                        transaction_assert_count += 1

                    elif value['ccy'] == execute_res['tradedCurrency']:
                        assert value['transactionType'] == 'TRADE_CREDIT', f"RfsHedgedOffPlatformTradeTransaction sell assert value['transactionType'] == 'TRADE_CREDIT', {value['transactionType']}, TRADE_CREDIT"
                        assert Decimal(str(value['amount'])) == Decimal(str(hedge_trade_amount)), f"RfsHedgedOffPlatformTradeTransaction sell assert Decimal(str(value['amount'])) == execute_res['quotedTradedCurrencyAmount'], {Decimal(str(value['amount']))} == {Decimal(str(hedge_trade_amount))}"
                        transaction_assert_count += 1

                    else:
                        logger.log(
                            f'[sell] RfsHedgedOffPlatformTradeTransaction AssertionError : christine.sze+oslsgexc@bc.group')

        for value in classified_data['altcoinx.RfsFloatTransaction']:
            if execute_res['buyTradedCurrency']:
                if value['account']['owner']['username'] == 'prakash.konagi+treasury_ds@osl.com':
                    if value['ccy'] == 'USD':
                        assert value['transactionType'] == 'FLOAT_DEBIT', f"RfsFloatTransaction buy assert value['transactionType'] == 'FLOAT_DEBIT', {value['transactionType']}, FLOAT_DEBIT"
                        # assert value['amount'] == platformTrade_Float_amount, f"RfsFloatTransaction buy {value['amount']} == {platformTrade_Float_amount}"
                        transaction_assert_count += 1

                    elif value['ccy'] == execute_res['tradedCurrency']:
                        assert value['transactionType'] == 'FLOAT_CREDIT', f"RfsFloatTransaction buy assert value['transactionType'] == 'FLOAT_CREDIT', {value['transactionType']}, FLOAT_CREDIT"
                        assert Decimal(str(value['amount'])) == Decimal(str(execute_res['quotedTradedCurrencyAmount'])), f"RfsFloatTransaction buy {Decimal(str(value['amount']))} == {Decimal(str(execute_res['quotedTradedCurrencyAmount']))}"
                        transaction_assert_count += 1

                    else:
                        logger.log(f'[buy] RfsFloatTransaction AssertionError : prakash.konagi+treasury_ds@osl.com')

                elif value['account']['owner']['username'] == 'billy.chan+ethdealer@osl.com':
                    if value['ccy'] == 'USD':
                        assert value['transactionType'] == 'FLOAT_CREDIT', f"RfsFloatTransaction buy assert value['transactionType'] == 'FLOAT_CREDIT', {value['transactionType']}, FLOAT_CREDIT"
                        # assert value['amount'] == platformTrade_Float_amount, f"RfsFloatTransaction buy {value['amount']} == {platformTrade_Float_amount}"
                        transaction_assert_count += 1

                    elif value['ccy'] == execute_res['tradedCurrency']:
                        assert value['transactionType'] == 'FLOAT_DEBIT', f"RfsFloatTransaction buy assert value['transactionType'] == 'FLOAT_DEBIT', {value['transactionType']}, FLOAT_DEBIT"
                        assert Decimal(str(value['amount'])) == Decimal(str(execute_res['quotedTradedCurrencyAmount'])), f"RfsFloatTransaction buy {Decimal(str(value['amount']))} == {Decimal(str(execute_res['quotedTradedCurrencyAmount']))}"
                        transaction_assert_count += 1

                    else:
                        logger.log(f'[buy] RfsFloatTransaction AssertionError : christine.sze+oslsgexc@bc.group')
            elif execute_res['buyTradedCurrency'] is False:
                if value['account']['owner']['username'] == 'prakash.konagi+treasury_ds@osl.com':
                    if value['ccy'] == 'USD':
                        assert value['transactionType'] == 'FLOAT_CREDIT', f"RfsFloatTransaction sell assert value['transactionType'] == 'FLOAT_CREDIT', {value['transactionType']}, FLOAT_CREDIT"
                        # assert value['amount'] == platformTrade_Float_amount, f"RfsFloatTransaction sell {value['amount']} == {platformTrade_Float_amount}"
                        transaction_assert_count += 1
                    elif value['ccy'] == execute_res['tradedCurrency']:
                        assert value['transactionType'] == 'FLOAT_DEBIT', f"RfsFloatTransaction sell assert value['transactionType'] == 'FLOAT_DEBIT', {value['transactionType']}, FLOAT_DEBIT"
                        assert Decimal(str(value['amount'])) == Decimal(str(execute_res['quotedTradedCurrencyAmount'])), f"RfsFloatTransaction sell {Decimal(str(value['amount']))} == {Decimal(str(execute_res['quotedTradedCurrencyAmount']))}"
                        transaction_assert_count += 1

                    else:
                        logger.log(f'[sell] RfsFloatTransaction AssertionError : prakash.konagi+treasury_ds@osl.com')
                elif value['account']['owner']['username'] == 'billy.chan+ethdealer@osl.com':
                    if value['ccy'] == "USD":
                        assert value['transactionType'] == 'FLOAT_DEBIT', f"RfsFloatTransaction sell assert value['transactionType'] == 'FLOAT_DEBIT', {value['transactionType']}, FLOAT_DEBIT"
                        # assert value['amount'] == platformTrade_Float_amount, f"RfsFloatTransaction sell {value['amount']} == {platformTrade_Float_amount}"
                        transaction_assert_count += 1

                    elif value['ccy'] == execute_res['tradedCurrency']:
                        assert value['transactionType'] == 'FLOAT_CREDIT', f"RfsFloatTransaction sell assert value['transactionType'] == 'FLOAT_CREDIT', {value['transactionType']}, FLOAT_CREDIT"
                        assert Decimal(str(value['amount'])) == Decimal(str(execute_res['quotedTradedCurrencyAmount'])), f"RfsFloatTransaction sell {Decimal(str(value['amount']))} == {Decimal(str(execute_res['quotedTradedCurrencyAmount']))}"
                        transaction_assert_count += 1

                    else:
                        logger.log(f'[sell] RfsFloatTransaction AssertionError : billy.chan+ethdealer@osl.com')

        if check_LP is True:
            assert transaction_assert_count == 16, f'transaction details assertion problem, should be 16, but got {transaction_assert_count}'
        elif transaction_assert_count != 16:
            logger.log(f'transaction details assertion problem, should be 16, but got {transaction_assert_count}', 'critical')

        logger.log('<===== assertion_ops_transaction_RFQ end =====>')
    except AssertionError as e:
        logger.log(f'assertion_ops_transaction_RFQ Assertion Error: {str(e)}', 'error')
        raise e
    except Exception as ex:
        logger.log(f'assertion_ops_transaction_RFQ Unknow Error：{str(ex)}', 'critical')
        raise ex



if __name__ == '__main__':
    check_rfs_LP_gateway()