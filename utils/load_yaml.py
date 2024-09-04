import yaml
import os

from utils.log import logger


def load_yaml_file(file_name):
    try:
        file_path = file_name + '.yaml'
        current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件的绝对路径所在目录
        file_path = os.path.join(current_dir, '..', 'testdata', file_path)
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        return data

    except Exception as ex:
        logger.log(f'load_yaml_file 发生未知异常：{str(ex)}', 'critical')
        raise ex


if __name__ == '__main__':
    # 读取YAML文件并转换成字典格式
    file_path = 'RFQ/test_sol'
    data_dict = load_yaml_file(file_path)
    # 打印转换后的字典数据
    print(data_dict)