from APIs.OPS_console.OPS_APIs import OPS_API
from APIs.OPS_console.OPS_Public import OpsPublic
from utils.random_output import generate_random_string
from utils.request_connect import make_request


class OPS_Deposit(OPS_API):
    def __init__(self):
        super().__init__()
        self.uuid = None

    def coin_deposit(self, currency, amount, account=None, uuid=None):
        if currency:
            currency = currency.upper()
        if account is None and uuid is None:
            raise ValueError("Either 'account' or 'uuid' must be provided.")
        if account:
            uuid = OpsPublic().listUser(account)
            self.uuid = uuid
        random_chara = generate_random_string()
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

    def fiat_deposit(self):
        pass

    def get_attribute(self, attribute_name):
        return getattr(self, attribute_name, None)


if __name__ == '__main__':
    print(OPS_Deposit().coin_deposit('Btc', 100, 'shawn.xiao@osl.com'))
