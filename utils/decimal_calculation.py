from decimal import Decimal, ROUND_HALF_UP, getcontext

from APIs.RFSconsole.RFS_APIs import RFS_API
from utils.ini_read import read_pytest_ini
from utils.log import logger


def round_to_decimal(value):
    try:
        # 确保 value 是 Decimal 类型
        if not isinstance(value, Decimal):
            value = Decimal(str(value))
        decimal_places = read_pytest_ini('decimal', 'global setting')
        # 计算需要的精度，decimal_places + 1 位小数
        rounding_precision = decimal_places + 1
        quantize_str = '1.' + '0' * rounding_precision
        quantize_value = Decimal(quantize_str)
        # 量化到 decimal_places + 1 位小数
        value_rounded = value.quantize(quantize_value, rounding=ROUND_HALF_UP)

        # 量化到 decimal_places 位小数
        final_quantize_str = '1.' + '0' * decimal_places
        final_quantize_value = Decimal(final_quantize_str)

        # 由于 ROUND_HALF_UP 可能会导致额外的进位，使用 ROUND_DOWN 处理最终值
        return value_rounded.quantize(final_quantize_value, rounding=ROUND_HALF_UP)
    except Exception as ex:
        logger.log(f'round_to_decimal Unknow Error：{str(ex)}', 'critical')
        raise ex

if __name__ == '__main__':
    # platformTrade_Float_amount = round_to_decimal((2.60876 * 1) / (1-0.0001-0.01) * (1-0.01))
    # print(platformTrade_Float_amount)
    # tran_list = RFS_API('stage').trades_completed()['data']
    # tran = tran_list[0]
    # Position = tran['Position']
    # P_SettlementAmount = round_to_decimal(Decimal(str(Position['TradedAmount'])) * Decimal(str(Position['limitPrice'])))
    # print(P_SettlementAmount)
    print(round_to_decimal(438338.623234 - 498676.445343))