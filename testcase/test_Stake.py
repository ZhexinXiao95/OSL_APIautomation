from decimal import Decimal

import allure

from APIs.OPS_console.OPS_Approval import OPS_Approval
from APIs.OPS_console.OPS_Stake import OpsStake


class Stake:
    def __init__(self, ccy, amount, account=False, uuid=False):
        self.ccy = ccy
        self.account = account
        self.uuid = uuid
        self.amount = amount

        self.balance_before_stake = None
        self.withdrawal_approveList = None
        self.balance_after_stake = None
    @allure.step("Ask for staking order")
    def stake_order(self):
        # stake前存储余额数据
        self.balance_before_stake = OpsStake().stakeBalance(self.ccy, account=self.account, uuid=self.uuid)
        assert self.balance_before_stake['code'] == '200', f"stakeBalance status got {self.balance_before_stake['code']}"

        # 提交ops订单
        order_dict = OpsStake().doStake(self.amount, self.account, self.uuid)
        assert order_dict['code'] == '200', f"doStake status got {order_dict['code']}"

        # 断言stakeAbleBalance减少
        self.balance_after_stake = OpsStake().stakeBalance(self.ccy, account=self.account, uuid=self.uuid)
        assert Decimal(self.balance_before_stake['stakeAbleBalance']) - Decimal(self.amount) == Decimal(self.balance_after_stake['stakeAbleBalance']), f"{Decimal(self.balance_before_stake['stakeAbleBalance'])} - {Decimal(self.amount)} == {Decimal(self.balance_after_stake['stakeAbleBalance'])}"

        # Withdrawal compliance approveList
        self.withdrawal_approveList = OPS_Approval().withdrawal_compliance_approveList(self.account)
        # Withdrawal approve
        OPS_Approval().withdrawal_compliance_approve(self.ccy, self.withdrawal_approveList['coinPaymentId'], self.withdrawal_approveList['uuid'])


    @allure.step("Ask for unstaking order")
    def unstake_order(self, amount):
        pass