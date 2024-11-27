from APIs.OPS_console.OPS_APIs import OPS_API
from APIs.OPS_console.OPS_Public import OpsPublic
from utils.ini_read import read_pytest_ini
from utils.request_connect import make_request
from datetime import datetime


class OpsStake(OPS_API):
    def __init__(self, account=None, uuid=None):
        super().__init__()
        if account is None and uuid is None:
            raise ValueError("Either 'account' or 'uuid' must be provided.")

        if uuid is None:
            # 如果没有提供 uuid，根据 account 获取 uuid
            uuid = OpsPublic().listUser(account)

        # 获取当前时间
        # 格式化时间为 'YYYY-MM-DDTHH:MM:SS' 格式
        self.current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        # 将 account 和 uuid 保存为实例属性
        self.account = account
        self.uuid = uuid

    def deposit(self, **kwargs):
        """
        Deposit to Staking Address - 存款到质押地址
        :param ccy:
        :param amount:
        :return:
        """
        # data = {
        #     "userUuid": self.uuid,
        #     "ccy": ccy,
        #     "amount": amount
        # }
        path = f"/v1/staking/pri/admin/tryStaking"
        response = make_request('post', path=self.host + path, params=kwargs, headers=self.headers_auth)
        return response

    def withdraw(self, **kwargs):
        """
        Withdrawal to Platform Address - 提款到平台地址
        :param ccy:
        :param amount:
        :return:
        """
        # data = {
        #     "userUuid": self.uuid,
        #     "ccy": ccy,
        #     "amount": amount
        # }
        path = f"/v1/staking/pri/admin/withdrawal"
        response = make_request('post', path=self.host + path, params=kwargs, headers=self.headers_auth)
        return response

    def stakeBalance(self, **kwargs):
        # if not isinstance(ccy, list):
        #     ccy = [ccy]
        # data = {
        #     "userUuid": self.uuid,
        #     "ccy": ccy
        # }
        path = f"/v1/staking/pri/admin/getBalanceByCcy"
        response = make_request('post', path=self.host + path, params=kwargs, headers=self.headers_auth)
        return response

    def stake(self, **kwargs):
        """
        Transfer available balance from Fireblock vault address to Staking contract address - 从Fireblock vault里可用余额转移到质押合约地址
        :param amount:
        :param ccy:
        :return:
        """
        # data = {
        #     "userUuid": self.uuid,
        #     "amount": amount,
        #     "ccy": ccy
        # }
        path = f"/v1/staking/pri/admin/stake"
        response = make_request('post', path=self.host + path, params=kwargs, headers=self.headers_auth)
        return response

    def unstake(self, **kwargs):
        """
        Withdraw current staking position from staking contract - 从质押合约中解除质押
        :param amount:
        :param ccy:
        :return:
        """
        # data = {
        #     "userUuid": self.uuid,
        #     "fireblocksPositionId": fireblocksPositionId,
        # }
        path = f"/v1/staking/pri/admin/unstake"
        response = make_request('post', path=self.host + path, params=kwargs, headers=self.headers_auth)
        return response

    def userProfit(self, **kwargs):
        """
        Get staking record by userUuid - 通过用户Uuid, 货币及Fireblock的Position Id获取用户利润
        :return:
        """
        # if not isinstance(ccy, list):
        #     ccy = [ccy]
        # data = {
        #     "userUuid": self.uuid,
        #     "ccy": ccy,
        #     "fireblocksPositionId": fireblocksPositionId
        # }
        path = f"/v1/staking/pri/admin/getUserProfit"
        response = make_request('post', path=self.host + path, params=kwargs, headers=self.headers_auth)
        return response

    def updateFireblockAction(self, **kwargs):
        """
        Update Fireblock Action - 通过Staking纪录id, 状态更新Staking Record数据的状态
        :return:
        """
        # data = {
        #     "id": record_id,
        #     "status": status,
        # }
        path = f"/v1/staking/pri/admin/updateFireblockAction"
        response = make_request('post', path=self.host + path, params=kwargs, headers=self.headers_auth)
        return response

    def stakingRecord(self, **kwargs):
        """
        Get Staking Record - 拮取Staking紀錄
        :return:
        """
        # data = {
        # }
        path = f"/v1/staking/pub/stakingRecord"
        response = make_request('get', path=self.host + path, params=kwargs, headers=self.headers_auth)
        return response

    def stakingRecordDetails(self, **kwargs):
        """
        Get Staking Record details from blotters and staking records, staking position - 從blotters, staking records和staking position拮取Staking紀錄明細
        :return:
        """
        # if dateTo is None:
        #     dateTo = self.current_time
        # if uuid is None:
        #     uuid = self.uuid
        host = "https://staking-service.stage.sg.osl-nucleus.io"
        # data = {
        #     "limit": 50,
        #     "offset": 0,
        #     "userUuid": uuid,
        #     "dateFrom": dateFrom,
        #     "dateTo": dateTo
        # }
        path = f"/v1/staking/pub/stakingRecordDetails"
        response = make_request('get', path=host + path, params=kwargs, headers=self.headers_auth)
        return response

    def stakingRecordsCount(self, **kwargs):
        """
        Get Staking Record details from blotters and staking records, staking position - 從blotters, staking records和staking position拮取Staking紀錄明細
        :return:
        """
        # if dateTo is None:
        #     dateTo = self.current_time
        # if uuid is None:
        #     uuid = self.uuid
        # data = {
        #     "limit": 50,
        #     "offset": 0,
        #     "userUuid": self.uuid,
        #     "dateFrom": dateFrom,
        #     "dateTo": dateTo
        # }
        host = "https://staking-service.stage.sg.osl-nucleus.io"
        path = f"/v1/staking/pub/stakingRecordsCount"
        response = make_request('get', path=host + path, params=kwargs, headers=self.headers_auth)
        return response

    def activePositions(self):
        """
        Get active staking position - 拮取生效中的Staking Position
        :return:
        """
        data = {
            "userUuid": self.uuid
        }
        path = f"/v1/staking/pub/activePositions"
        response = make_request('get', path=self.host + path, params=data, headers=self.headers_auth)
        return response


    def external_network_overview(self):
        rated_apikey = read_pytest_ini("rated_apikey", "external")
        host = 'https://api.rated.network'
        path = "/v0/eth/network/overview"
        headers = {
            "X-Rated-Network": "holesky",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {rated_apikey}"
        }
        response = make_request('get', path=host + path, headers=headers)
        return response

if __name__ == '__main__':
    Stake = OpsStake('selceo1@snapmail.cc')
    # dateFrom = datetime(2024, 11, 1, 16, 0, 0).strftime('%Y-%m-%dT%H:%M:%S')
    # data = {
    #     "userUuid": Stake.uuid,
    #     "ccy": 'ETH',
    #     "amount": "33"
    # }
    # Stake.deposit(**data)
    # print(Stake.deposit('ETH',"31"))
    # print(Stake.withdraw('ETH',"1"))
    # print(Stake.stakeBalance('ETH'))
    # print(Stake.stake('ETH',"32"))
    # print(Stake.unstake(""))
    # print(Stake.userProfit("ETH"))
    data = {}
    print(Stake.stakingRecord(**data))
    # print(Stake.stakingRecordDetails(dateFrom))
    # print(Stake.stakingRecordsCount(dateFrom))
    # print(Stake.activePositions())