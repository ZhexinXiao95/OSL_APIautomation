from APIs.OPS_console.OPS_APIs import OPS_API
from APIs.OPS_operation import OPS_operation




if __name__ == '__main__':
    OPS_API().ops_authToken()
    OPS_operation().account_deposit('HKD', 100, 'shawn.xiao@osl.com')
