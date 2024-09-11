from APIs.OPS_console.OPS_APIs import OPS_API
from APIs.OPS_console.OPS_Approval import OPS_Approval
from APIs.OPS_console.OPS_Public import OpsPublic
from APIs.OPS_console.OPS_deposit import OPS_Deposit
from utils.decimal_calculation import RTD
from utils.log import logger


class OPS_operation:
    def __init__(self):
        pass

    def account_deposit(self, currency, amount, account=None, uuid=None):
        Deposit_Obj = OPS_Deposit()
        approval_id = Deposit_Obj.deposit(currency, amount, account, uuid)['uuid']
        uuid = Deposit_Obj.get_attribute('uuid')
        currency_type = Deposit_Obj.get_attribute('currency_type')
        balance_before = OpsPublic().account_balance(uuid, currency)
        Approval_Obj = OPS_Approval()
        approval = Approval_Obj.approvalList(currency_type)[0]
        # 检查审批信息
        Approval_Obj.assertion_approvalList(approval_id, approval, account, uuid, amount, currency, currency_type)
        # 审批操作
        OPS_Approval().ticket_approve(currency_type, approval_id)
        # 校验余额增加
        balance_after = OpsPublic().account_balance(uuid, currency)
        logger.log(f'{balance_before}', 'critical')
        logger.log(f'{balance_after}', 'critical')

        assert RTD(balance_before) + RTD(amount) == RTD(balance_after), f"balance incorrect, balance before:{RTD(balance_before)} + deposit amount:{RTD(amount)} == balance after:{RTD(balance_after)}"
        logger.log(f'Account:[{account}] \nUuid:[{uuid}] \nCurrency:[{currency}] \nAmount:[{amount}] \naccount deposit successful')

if __name__ == '__main__':
    OPS_API().ops_authToken()
    OPS_operation().account_deposit('HKD',100,'shawn.xiao@osl.com')
