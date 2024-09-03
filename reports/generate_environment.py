import platform
from utils.log import logger
import subprocess
from utils.ini_read import *
import platform

def get_system_version():
    system = platform.system()
    if system == 'Darwin':
        return 'Mac'
    else:
        return system


def get_allure_version():
    try:
        # 运行命令 `allure --version` 并捕获输出
        result = subprocess.run(['allure', '--version'], capture_output=True, text=True, check=True)
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        logger.log(f"Error: {e}",'error')

def generate_environment_file():
    system_version = get_system_version()
    python_version = platform.python_version()
    env = read_pytest_ini('env',  'global setting')
    allureVersion = get_allure_version()
    baseUrl = read_pytest_ini('api_host', env)
    account = read_pytest_ini('test_account', env)
    venus = read_pytest_ini('venus', env)
    # Check if environment.properties file exists and delete it if it does
    if os.path.exists('./reports/allure-results/environment.properties'):
        os.remove('./reports/allure-results/environment.properties')

    with open('./reports/allure-results/environment.properties', 'w') as f:
        f.write(f'AccountUse = {account}\n'
                f'Gateway = {venus}\n'
                f'TestEnvironment = {env}\n'
                f'systemVersion = {system_version}\n'
                f'PythonVersion = {python_version}\n'
                f'allureVersion = {allureVersion}\n'
                f'baseUrl = {baseUrl}\n'
                f'projectName = RFQ api testing\n'
                f'author = Shawn Xiao\n')




if __name__ == '__main__':
    generate_environment_file()