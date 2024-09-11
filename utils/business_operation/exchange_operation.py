from APIs.user.Exchange import get_exchange_currency_pairs
from utils.decimal_calculation import RTD
from utils.log import logger


def price_for_limit(side, symbol):
    """
    TODO: 如果价格相差太小，需要清理数据, 思路用orderbook接口查看对应qty，进行吃单
    TODO: 如果价格没有，需要下单
    """
    # 获取合适的买卖价格
    price = fills_price(side, symbol)
    # # 如果价格相差太小，需要清理数据
    # if RTD(askPrice) - RTD(bidPrice) < 2:
    #     pass
    if side == 'Buy':
        price = RTD(price) - 2
    else:
        price = RTD(price) + 2
    return str(price)


def fills_price(side, symbol):
    # 获取最新的买卖价格
    res = get_exchange_currency_pairs(symbol)['res']
    bidPrice = res[0]['bidPrice']
    askPrice = res[0]['askPrice']
    logger.log(f'bidPrice: {bidPrice}, askPrice: {askPrice}')
    if side == 'Buy':
        return askPrice
    elif side == 'Sell':
        return bidPrice
    else:
        return askPrice, bidPrice

if __name__ == '__main__':
    a = price_for_limit('Buy', 'BTCUSD')
    print(type(a))
    print(str(a))
