import requests
from utils.Authenticator import authenticator_code
from utils.ini_read import read_pytest_ini, write_pytest_ini

host = read_pytest_ini('rfs_console_host', 'stage')


def rfs_authToken(env):
    current_otp = authenticator_code('rfs_console_authenticator', env)
    account, pwd = read_pytest_ini("rfs_console_acct", env)
    cookie = read_pytest_ini("rfs_console_cookie", env)
    headers = {
        'content-type': 'application/json',
        'cookie': cookie
    }
    path = "/ui/auth"
    data = {
        "username": account,
        "password": pwd,
        "otp": current_otp
    }
    response = requests.post(url=host + path, headers=headers, json=data)
    assert response.json()
    assert response.status_code == 200, f'rfs_authToken api request receive {response.status_code}'
    write_pytest_ini('rfs_console_token', env, response.json()['authToken'])
    return response.json()['authToken']


if __name__ == '__main__':
    print(rfs_authToken('stage'))
