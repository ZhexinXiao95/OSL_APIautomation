import time
import pytest
from utils.RFQ_relates_function import *
from utils.ini_read import read_pytest_ini, write_pytest_ini
from utils.log import logger


@pytest.fixture(autouse=True)
def setup_and_teardown():
    logger.log("Test START")
    yield

    # 执行测试后的清理操作
    logger.log("Test END")


@pytest.fixture
def rfq_order_before_check():
    RFS_API(env).rfs_authToken()
    OPS_API(env).ops_authToken()
    check_rfs_trading_status()
    check_rfs_LP_gateway()

