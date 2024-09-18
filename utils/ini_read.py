import configparser
import os

from utils.log import logger

config = configparser.ConfigParser()
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pytest.ini')  # 上级目录的 logs 文件夹
config.read(file_path)


def read_pytest_ini(key, env):
    try:
        # 读取示例中的 [pytest] 部分的配置项
        if env in config:
            if key in config[env]:
                value = config[env][key]
                if "|" in value:
                    value = value.split("|")
                    return value
                return value
        else:
            raise Exception

    except Exception as ex:
        logger.log(f'read_pytest_ini 1{key} {env} 发生未知异常：{str(ex)}', 'critical')
        raise ex


def write_pytest_ini(key, env, value):
    try:
        config.read(file_path)

        if not config.has_section(env):
            config.add_section(env)

        config.set(env, key, value)

        with open(file_path, 'w') as configfile:
            config.write(configfile)
            logger.log(f'Successfully wrote {key}={value} to {env} section in pytest.ini')

    except Exception as ex:
        logger.log(f'write_pytest_ini encountered an error: {str(ex)}', 'error')
        raise ex


if __name__ == '__main__':
    print(read_pytest_ini('api_host', 'stage'))
    # print(read_pytest_ini('rfs_console_authenticator', 'stage'))
    # write_pytest_ini('rfs_console_token','stage','123')