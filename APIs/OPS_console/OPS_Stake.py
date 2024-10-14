from APIs.OPS_console.OPS_APIs import OPS_API
from APIs.OPS_console.OPS_Public import OpsPublic
from utils.request_connect import make_request


class OpsStake(OPS_API):
    def __init__(self, account=None, uuid=None):
        super().__init__()
        if account is None and uuid is None:
            raise ValueError("Either 'account' or 'uuid' must be provided.")

        if uuid is None:
            # 如果没有提供 uuid，根据 account 获取 uuid
            uuid = OpsPublic().listUser(account)

        # 将 account 和 uuid 保存为实例属性
        self.account = account
        self.uuid = uuid

    def stakeBalance(self, ccy):
        if not isinstance(ccy, list):
            ccy = [ccy]
        data = {
            "userUuid": self.uuid,
            "ccy": ccy
        }
        path = f"/v1/staking/pri/admin/getBalanceByCcy"
        response = make_request('post', path=self.host + path, params=data, headers=self.headers_auth)
        return response

    def doStake(self, amount):
        data = {
            "userUuid": self.uuid,
            "amount": amount,
            "ccy": "ETH"
        }
        path = f"/v1/staking/pri/admin/doStake"
        response = make_request('post', path=self.host + path, params=data, headers=self.headers_auth)
        return response

    def userProfit(self):
        data = {
            "email": "888",
            "userUuid": self.uuid,
            "ccy": [
                "ETH"
            ]
        }
        path = f"/v1/staking/pri/admin/doStake"
        response = make_request('post', path=self.host + path, params=data, headers=self.headers_auth)
        return response

if __name__ == '__main__':
    # print(OpsStake().stakeBalance('ETH', 'selceo1@snapmail.cc'))
    print(OpsStake(account='selceo1@snapmail.cc').stakeBalance('ETH'))