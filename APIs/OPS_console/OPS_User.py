from APIs.OPS_console.OPS_APIs import OPS_API
from APIs.OPS_console.OPS_Public import OpsPublic
from utils.request_connect import make_request


class OpsUser(OPS_API):

    def buyTradeRestriction_disable(self, account=None, uuid=None):
        if account is None and uuid is None:
            raise ValueError("Either 'account' or 'uuid' must be provided.")
        if uuid is None:
            uuid = OpsPublic().listUser(account)
        data = {
            "value": "disabled"
        }
        path = f"/opUser/{uuid}/buyTradeRestriction/disable"
        print(self.headers_auth)
        response = make_request('post', path=self.host + path, params=data, headers=self.headers_auth)
        return response




if __name__ == '__main__':
    # OPS_API().ops_authToken()
    print(OpsUser().buyTradeRestriction_disable(account='shawn.xiao@osl.com'))
