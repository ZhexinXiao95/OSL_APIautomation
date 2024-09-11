import ast
import os
import json
import shutil
from datetime import datetime
import pytest
from reports.customize_allure import allure_edit, find_last_html
from utils.email_ import send_email
from utils.file_delete import delete_oldest_html_files, delete_oldest_logs_files
from utils.ini_read import read_pytest_ini
from utils.log import logger

if __name__ == '__main__':
    # 生成Allure报告
    # os.system('pytest --clean-alluredir --alluredir=./reports/allure-results')
    # 跑所有test
    # pytest.main(['-s', '-q', './', '--clean-alluredir', '--alluredir=./reports/allure-results'])
    # 跑指定test
    # pytest.main(['-s', '-q', './testcase/test_ExchangeOrder.py', '--clean-alluredir', '--alluredir=./reports/allure-results'])
    # 跑指定方法
    # pytest.main(['-s', '-q', './testcase/test_ExchangeOrder.py::test_PostOnly_FillsOrder', '--clean-alluredir', '--alluredir=./reports/allure-results'])

    test_suite = read_pytest_ini('test_suite', 'global setting')
    if test_suite == 'all':
        logger.log('Test All Test Cases')
        pytest.main(['-s', '-q', './', '--clean-alluredir', '--alluredir=./reports/allure-results'])
    elif test_suite == 'specified':
        test_name = read_pytest_ini('test_name', 'global setting')
        logger.log(f'Test {test_name} Cases')
        pytest.main(['-s', '-q', f'./testcase/{test_name}', '--clean-alluredir', '--alluredir=./reports/allure-results'])
    elif test_suite == 'method':
        test_name = read_pytest_ini('test_name', 'global setting')
        test_method = read_pytest_ini('test_method', 'global setting')
        logger.log(f'Test Method {test_method} in {test_name} Cases')
        pytest.main(['-s', '-q', f'./testcase/{test_name}::{test_method}', '--clean-alluredir', '--alluredir=./reports/allure-results'])
    else:
        logger.log('empty folder')
    allure_edit()
    reports_path = 'reports/history_reports/'
    delete_oldest_html_files(reports_path)
    delete_oldest_logs_files('./logs/')
    decision = ast.literal_eval(read_pytest_ini('send_email', 'global setting'))
    if decision:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file_path = reports_path + find_last_html("./reports/history_reports/")
        # 发送报告邮件
        send_email(f'Allure-report {current_time}', f'{current_time}', file_path)
    else:
        logger.log('Not need to send email...')
    # # 打开报告
    # # open_command = "allure open"
    # # os.system(open_command)
