from APIs.OPS_console.OPS_APIs import OPS_API
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

if __name__ == '__main__':
    OPS_Approval().ManualCoinPaymentDeposit_list()