from APIs.OPS_console.OPS_APIs import OPS_API
from utils.decimal_calculation import RTD
from utils.path_concatenation import get_concatenation
from utils.request_connect import make_request


class OPS_Approval(OPS_API):

    def ManualCoinPaymentDeposit_list(self, status='PENDING', limit=50):
        data = {
            "approvalStatus": status,
            "limit": limit,
            "offset": 0
        }
        path = "/opsApproval/ApprovalRequest/ManualCoinPaymentDeposit" + get_concatenation(data)
        response = make_request('get', path=self.host + path, headers=self.headers_auth)
        return response

    def ManualCoinPaymentDeposit_approve(self, value):
        if not isinstance(value, list):
            value = [value]
        data = {
            "approveList": value
        }
        path = "/opsApproval/ApprovalRequest/ManualCoinPaymentDeposit/do/approve"
        response = make_request('post', path=self.host + path, params=data, headers=self.headers_auth)
        return response

    def FiatDeposit_approvalList(self, status='DEPOSIT_PENDING_FOUR_EYES', limit=10):
        data = {
            "includeApproverUser": True,
            "includeOperatorUser": True,
            "limit": limit,
            "paymentState": status,
            "includeUserDeclarationFormFilled": True
        }

        path = "/Deposit" + get_concatenation(data)
        response = make_request('get', path=self.host + path, headers=self.headers_auth)
        return response

    def FiatDeposit_approve(self, value):
        path = "/Deposit/" + str(value) + '/do/processDeposit'
        response = make_request('post', path=self.host + path, headers=self.headers_auth)
        return response

    def approvalList(self, currency_type):
        if currency_type == 'crypto':
            return self.ManualCoinPaymentDeposit_list()
        elif currency_type == 'fiat':
            return self.FiatDeposit_approvalList()

    def ticket_approve(self, currency_type, value):
        if currency_type == 'crypto':
            return self.ManualCoinPaymentDeposit_approve(value)
        elif currency_type == 'fiat':
            return self.FiatDeposit_approve(value)

    def assertion_approvalList(self, approval_id, approval, account, uuid, amount, currency, currency_type):
        if currency_type == 'crypto':
            assert approval['approvalRequest'][
                       'id'] == approval_id, f"Approval ID not match, {approval['approvalRequest']['id']} not match {approval_id}"
            if account:
                assert approval['manualCoinPaymentDepositDetail'][
                           'username'] == account, f"Approval ID not match, {approval['manualCoinPaymentDepositDetail']['username']} not match {account}"
            elif uuid:
                assert approval['manualCoinPaymentDepositDetail'][
                           'userUuid'] == uuid, f"uuid not match, {approval['manualCoinPaymentDepositDetail']['userUuid']} not match {uuid}"
            assert RTD(approval['manualCoinPaymentDepositDetail']['amount']) == RTD(
                amount), f"amount not match, {RTD(approval['manualCoinPaymentDepositDetail']['amount'])} not match {RTD(amount)}"
            assert approval['manualCoinPaymentDepositDetail'][
                       'ccy'] == currency.upper(), f"ccy not match, {approval['manualCoinPaymentDepositDetail']['ccy']} not match {currency.upper()}"
        elif currency_type == 'fiat':
            assert approval['uuid'] == approval_id, f"Approval ID not match, {approval['uuid']} not match {approval_id}"
            if account:
                assert approval['user']['username'] == account, f"Approval ID not match, {approval['user']['username']} not match {account}"
            elif uuid:
                assert approval['user']['uuid'] == uuid, f"uuid not match, {approval['user']['uuid'] == uuid} not match {uuid}"
            assert RTD(approval['amount']) == RTD(amount), f"amount not match, {RTD(approval['amount'])} not match {RTD(amount)}"
            assert approval['ccy'] == currency.upper(), f"ccy not match, {approval['ccy']} not match {currency.upper()}"


if __name__ == '__main__':
    OPS_Approval().ManualCoinPaymentDeposit_list()
