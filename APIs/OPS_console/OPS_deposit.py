from APIs.OPS_console.OPS_APIs import OPS_API
from APIs.OPS_console.OPS_Public import OpsPublic
from utils.log import logger
from utils.path_concatenation import get_concatenation
from utils.random_output import generate_random_string
from utils.request_connect import make_request


class OPS_Deposit(OPS_API):
    def __init__(self):
        super().__init__()
        self.uuid = None
        self.currency_type = None

    def deposit(self, currency, amount, account=None, uuid=None):
        if currency:
            currency = currency.upper()
        if account is None and uuid is None:
            raise ValueError("Either 'account' or 'uuid' must be provided.")
        if account:
            uuid = OpsPublic().listUser(account)
            self.uuid = uuid
        currency_type = self.explore_currency_type(currency)
        random_chara = generate_random_string()
        if currency_type == 'crypto':
            return self.coin_deposit(currency, amount, random_chara, uuid)
        elif currency_type == 'fiat':
            return self.fiat_deposit(currency, amount, random_chara, uuid)
        else:
            logger.log(f'currency_type is {currency_type}, cannot find the {currency} to deposit')

    def coin_deposit(self, currency, amount, random_chara, uuid=None):
        data = {
            "userUuid": uuid,
            "accountGroupUuid": uuid,
            "ccy": currency,
            "amount": amount,
            "transactionHash": random_chara,
            "operatorComment": 'null',
            "custodyTransactionId": random_chara
        }
        path = "/Deposit/manualCoinDeposit/processDeposit"
        response = make_request('post', path=self.host + path, params=data, headers=self.headers_auth)
        return response

    def fiat_deposit(self, currency, amount, random_chara, uuid=None):
        data = {
            "userUuid": uuid,
            "depositMethod": "CASH_DEPOSIT",
            "ccy": currency,
            "amount": amount,
            "fee": "0.00",
            "optionalReference": random_chara,
            "operatorComment": None,
            "companyBankAccount": "BoComm - Client cash - USD (AE)",
            "accountGroupUuid": uuid
        }
        path = "/Deposit/cashDeposit/processDeposit"
        response = make_request('post', path=self.host + path, params=data, headers=self.headers_auth)
        return response

    def get_ccy_list(self, showCrypto=None, showFiat=None, limit=200):
        if showCrypto is None and showFiat is None:
            raise ValueError("Either 'showCrypto' or 'showFiat' must be provided.")

        data = {
            "showCrypto": showCrypto,
            'showFiat': showFiat,
            'limit': limit,
        }
        path = "/opConfig/simpleType/CcyEnum" + get_concatenation(data)
        response = make_request('get', path=self.host + path, headers=self.headers_auth)
        return response

    def explore_currency_type(self, currency):
        fiat_list = self.get_ccy_list(showFiat=True)
        crypto_list = self.get_ccy_list(showCrypto=True)
        for value in fiat_list:
            if value['name'] == currency:
                self.currency_type = 'fiat'

        for value in crypto_list:
            if currency == value['name']:
                self.currency_type = 'crypto'

        if self.currency_type is None:
            raise ValueError(f"The currency '{currency}' is not found in either Fiat or Crypto List.")
        return self.currency_type

    def get_attribute(self, attribute_name):
        return getattr(self, attribute_name, None)


if __name__ == '__main__':
    # print(OPS_Deposit().get_ccy_list(showFiat=True))
    # print(OPS_Deposit().coin_deposit('Btc', 100, 'shawn.xiao@osl.com'))
    OPS_Deposit().deposit('HKD',100,'shawn.xiao@osl.com')