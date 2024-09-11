from APIs.OPS_console.OPS_Approval import OPS_Approval
from APIs.OPS_console.OPS_Public import OpsPublic
from APIs.OPS_console.OPS_deposit import OPS_Deposit
from utils.decimal_calculation import RTD
from utils.log import logger


class OPS_operation:
    def __init__(self):
        pass

    def coin_deposit(self, currency, amount, account=None, uuid=None):
        deposit = OPS_Deposit()
        id = deposit.coin_deposit(currency, amount, account, uuid)['uuid']
        uuid = deposit.get_attribute('uuid')
        balance_before = OpsPublic().account_balance(uuid, currency)
        approval = OPS_Approval().ManualCoinPaymentDeposit_list()[0]
        print(approval)
        assert approval['approvalRequest']['id'] == id, f"Approval ID not match, {approval['approvalRequest']['id']} not match {id}"
        if account:
            assert approval['manualCoinPaymentDepositDetail']['username'] == account, f"Approval ID not match, {approval['manualCoinPaymentDepositDetail']['username']} not match {account}"
        elif uuid:
            assert approval['manualCoinPaymentDepositDetail']['userUuid'] == uuid, f"uuid not match, {approval['manualCoinPaymentDepositDetail']['userUuid']} not match {uuid}"
        assert RTD(approval['manualCoinPaymentDepositDetail']['amount']) == RTD(amount), f"amount not match, {RTD(approval['manualCoinPaymentDepositDetail']['amount'])} not match {RTD(amount)}"
        assert approval['manualCoinPaymentDepositDetail']['ccy'] == currency.upper(), f"ccy not match, {approval['manualCoinPaymentDepositDetail']['ccy']} not match {currency.upper()}"
        OPS_Approval().ManualCoinPaymentDeposit_approve(id)
        balance_after = OpsPublic().account_balance(uuid, currency)
        assert RTD(balance_before) + RTD(amount) == RTD(balance_after), f"balance incorrect, balance before:{RTD(balance_before)} + deposit amount:{RTD(amount)} == balance after:{RTD(balance_after)}"
        logger.log(f'Account:[{account}] Uuid:[{uuid}] Currency:[{currency}] Amount:[{amount}] Coin deposit successful')

if __name__ == '__main__':
    OPS_operation().coin_deposit('BTC',100,'shawn.xiao@osl.com')
