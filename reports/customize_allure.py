import os
import os
import json
import shutil
from datetime import datetime
import pytest
from utils.email_ import send_email
from reports.generate_environment import generate_environment_file
from utils.log import logger


def change_allure_report():
    # 修改标题
    aim_summary = os.path.join('./reports/allure-report', 'widgets', 'summary.json')
    operate_key(aim_summary, "Allure Report", "OSL Automation Report", "replace_key")
    # 修改浏览器窗口标题
    aim_index = os.path.join('./reports/allure-report', 'index.html')
    operate_key(aim_index, "Allure Report", "OSL Automation Report", "replace_key")


def operate_key(aim_file, aim_key, new_key, aim_type):
    """
    :param aim_file: 目标文件
    :param aim_key: 目标关键字
    :param new_key: 需要替换成
    :param aim_type: 需要使用关键字做什么
    """
    # 打开文件
    with open(aim_file, 'r+', encoding="utf-8") as f:
        # 读取当前文件的所有内容
        all_the_lines = f.readlines()
        f.seek(0)
        f.truncate()
        # 循环遍历每一行的内容
        for line in all_the_lines:
            need_write = True
            # 如果目标关键字包含在line中
            if aim_key in line:
                if aim_type == 'replace_key':
                    # 则替换line为new_line
                    f.write(line.replace(aim_key, new_key))  # 替换关键词
                    need_write = False
                elif aim_type == "replace_line":
                    f.write(line.replace(line, new_key + '\n'))  # 替换关键句
                    need_write = False
                elif aim_type == "insert_line":
                    f.write(new_key + '\n')  # 在找到的位置插入新标签，并且仅当需要插入时
                    f.write(line)
                    need_write = False
            if len(all_the_lines) and need_write:
                f.write(line)
        # 关闭文件
        f.close()


def get_dirname():
    hostory_file = os.path.join(ALLURE_PLUS_DIR, "history.json")
    if os.path.exists(hostory_file):
        with open(hostory_file) as f:
            li = eval(f.read())
        # 根据构建次数进行排序，从大到小
        li.sort(key=lambda x: x['buildOrder'], reverse=True)
        # 返回下一次的构建次数，所以要在排序后的历史数据中的buildOrder+reports
        return li[0]["buildOrder"] + 1, li
    else:
        # 首次进行生成报告，肯定会进到这一步，先创建history.json,然后返回构建次数1（代表首次）
        with open(hostory_file, "w") as f:
            pass
        return 1, None


def update_trend_data(dirname, old_data: list):
    """
    dirname：构建次数
    old_data：备份的数据
    update_trend_data(get_dirname())
    """
    allure_report_path = './reports/allure-report/widgets'
    WIDGETS_DIR = allure_report_path
    # 在reports文件夹下面创建相对应的构建次数文件夹
    folder_path = f"./reports/history_results/{dirname}"
    # os.makedirs(folder_path)

    # 将allure-report中的所有文件复制到对应构建次数的文件夹中
    # 定义源文件夹路径
    source_folder = "./reports/allure-report"
    # 定义目标文件夹路径
    target_folder = folder_path
    # 复制源文件夹中的所有文件和子文件夹到目标文件夹
    shutil.copytree(source_folder, target_folder)

    # 读取最新生成的history-trend.json数据
    with open(os.path.join(WIDGETS_DIR, "history-trend.json")) as f:
        data = f.read()

    new_data = eval(data)
    if old_data is not None:
        new_data[0]["buildOrder"] = old_data[0]["buildOrder"] + 1
    else:
        old_data = []
        new_data[0]["buildOrder"] = 1
    # 给最新生成的数据添加reportUrl key，reportUrl要根据自己的实际情况更改
    new_data[0]["reportUrl"] = f""
    # 把最新的数据，插入到备份数据列表首位
    old_data.insert(0, new_data[0])

    # 把所有生成的报告中的history-trend.json都更新成新备份的数据old_data，这样的话，点击历史趋势图就可以实现新老报告切换
    for i in range(1, dirname + 1):
        with open(os.path.join(ALLURE_PLUS_DIR, f"{str(i)}/widgets/history-trend.json"), "w+") as f:
            f.write(json.dumps(old_data))
    with open(os.path.join(allure_report_path, "history-trend.json"), "w+") as f:
        f.write(json.dumps(old_data))
    # 把数据备份到history.json
    hostory_file = os.path.join(ALLURE_PLUS_DIR, "history.json")
    with open(hostory_file, "w+") as f:
        f.write(json.dumps(old_data))
    return old_data, new_data[0]["reportUrl"]


ALLURE_PLUS_DIR = r"./reports/history_results"

def allure_edit():
    # 增加环境信息
    generate_environment_file()
    # 先调用get_dirname()，获取到这次需要构建的次数和json信息
    buildOrder, old_data = get_dirname()
    # 再执行命令行
    # 对生成的Allure报告进行进一步演进（生成一个相对独立的报告静态工程）
    # ALLURE_PLUS_DIR 是存放要生成的details记录
    # buildOrder 是表示以构建次数为文件夹名称
    os.system("allure generate ./reports/allure-results --clean -o ./reports/allure-report")
    # 自定义修改report样式
    change_allure_report()
    # 执行完毕后再调用update_trend_data()生成allure报告的trend记录（历史运行结果）
    all_data, reportUrl = update_trend_data(buildOrder, old_data)
    # 利用插件输出可独立阅览的html文件
    os.system("allure-combine ./reports/allure-report --dest ./reports/allure-report")
    current_time = datetime.now().strftime('%Y_%m_%d %H_%M_%S')
    shutil.move("./reports/allure-report/complete.html",'./reports/history_reports/')
    os.rename("./reports/history_reports/complete.html", f"./reports/history_reports/{current_time}.html")

def find_last_html(directory):
    # 列出目录下所有文件
    files = os.listdir(directory)

    # 筛选出所有的HTML文件，并获取最新的文件
    latest_file = None
    latest_mtime = None

    for file in files:
        if file.endswith('.html'):
            file_path = os.path.join(directory, file)
            file_mtime = os.path.getmtime(file_path)
            if latest_mtime is None or file_mtime > latest_mtime:
                latest_mtime = file_mtime
                latest_file = file

    # 如果找到最新的HTML文件，则输出文件名
    if latest_file:
        logger.log(f"最新生成的HTML文件是:{latest_file}")
        return latest_file
    else:
        logger.log("目录中未找到HTML文件")




if __name__ == '__main__':
    path = './reports/history_reports'

