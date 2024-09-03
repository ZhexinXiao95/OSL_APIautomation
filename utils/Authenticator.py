import pyotp

from utils.ini_read import read_pytest_ini
from utils.log import logger


def authenticator_code(name, env):
    try:
        acct_auth = read_pytest_ini(name, env)
        account, secret = acct_auth[0], acct_auth[1]
        totp = pyotp.TOTP(secret)
        current_otp = totp.now()
        logger.log(f'{account}Authenticator_code return [{current_otp}]')
        return current_otp
    except Exception as e:
        logger.log(f"authenticator_code unknow error {str(e)}, using {name}, {env}")
        raise e

if __name__ == '__main__':
    print(authenticator_code('authenticator','stage_rfs_console'))