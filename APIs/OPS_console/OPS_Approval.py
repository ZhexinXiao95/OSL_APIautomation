from APIs.OPS_console.OPS_APIs import OPS_API
from utils.decimal_calculation import RTD
from utils.path_concatenation import get_concatenation
from utils.request_connect import make_request
from datetime import datetime, timezone

# 获取当前时间
now = datetime.now(timezone.utc)
day = now.day
today_start_time = now.replace(day=day-1, hour=16, minute=0, second=0, microsecond=0)
today_end_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
# 格式化成指定的字符串格式
today_start = today_start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
today_end = today_end_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
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
                assert approval['user'][
                           'username'] == account, f"Approval ID not match, {approval['user']['username']} not match {account}"
            elif uuid:
                assert approval['user'][
                           'uuid'] == uuid, f"uuid not match, {approval['user']['uuid'] == uuid} not match {uuid}"
            assert RTD(approval['amount']) == RTD(
                amount), f"amount not match, {RTD(approval['amount'])} not match {RTD(amount)}"
            assert approval['ccy'] == currency.upper(), f"ccy not match, {approval['ccy']} not match {currency.upper()}"

    def withdrawal_compliance_approveList(self, username, limit=50):
        data = {
            "username": username,
            "transactionType": "WITHDRAWAL",
            "limit": limit,
            "dateFrom": today_start,
            "dateTo": today_end
        }

        path = "/Withdrawal/coin/pendingSubCheck" + get_concatenation(data)
        response = make_request('get', path=self.host + path, headers=self.headers_auth)
        return response

    def withdrawal_compliance_approve(self, ccy=None, paymentId=None, coinAddress=None, approval_uuid=None, username=None, approval_type=False,
                                      multiple=True, firstApproval=True):
        if firstApproval:
            if username is None:
                raise ValueError("Either 'username' must be provided.")
            list_res = self.withdrawal_compliance_approveList(username)
            ccy = list_res[0]['coinTransaction']['ccy']
            paymentId = list_res[0]['coinPaymentId']
            coinAddress = list_res[0]['coinTransaction']['coinAddress']
            approval_uuid = list_res[0]['coinTransaction']['uuid']
        else:
            if ccy is None or paymentId is None or coinAddress is None or approval_uuid is None:
                raise ValueError("Either 'ccy' or 'paymentId' or 'coinAddress' or 'approval_uuid' must be provided.")

        if multiple:
            approval_type_list = ['COIN_PURITY', 'SUSP_CHECK', 'VASP_CHECK', 'WITHDRAWAL_UNLOCK']
        else:
            if not approval_type:
                raise ValueError("withdrawal_compliance - approval_type不能为空")
            if not isinstance(approval_type, list):
                approval_type_list = [approval_type]
        path = "/Withdrawal/coin/pendingSubCheck/do/approve"
        for approval_type in approval_type_list:
            data = {
                "ccy": ccy,
                "paymentId": paymentId,
                "coinAddress": coinAddress,
                "type": approval_type,
                "uuid": approval_uuid
            }
            response = make_request('post', path=self.host + path, params=data, headers=self.headers_auth)
            assert response['coinPurity']['state'] == 'APPROVED', 'did not get approved'


if __name__ == '__main__':
    # OPS_API().ops_authToken()
    # OPS_Approval().FiatDeposit_approve('6044b033-69a3-4389-a81c-f8aeafcf2960')
    # OPS_Approval().withdrawal_compliance_approve('ETH', '1165880', '0xC122b72D9A09B9297797deB6FaEA192C6Ed8174B',
    #                                              'af28102c-6ae0-4cc5-a6bb-7407f218c42e', multiple=True)
    # OPS_Approval().withdrawal_compliance_approveList('selceo1@snapmail.cc')
    OPS_Approval().withdrawal_compliance_approve(username="selceo1@snapmail.cc")