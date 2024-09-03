import os

from utils.log import logger


def delete_oldest_html_files(directory, max_files=10):
    # 获取目录下所有 HTML 文件的路径
    html_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.html')]

    # 按修改时间排序
    html_files.sort(key=os.path.getmtime)

    # 如果文件数超过最大限制，删除最早的文件
    if len(html_files) > max_files:
        for file_to_delete in html_files[:len(html_files) - max_files]:
            os.remove(file_to_delete)
            logger.log(f"RepoDeleted: {file_to_delete}")


def delete_oldest_logs_files(directory, max_files=10):
    # 获取目录下所有 log 文件的路径
    log_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.log')]

    # 按修改时间排序
    log_files.sort(key=os.path.getmtime)

    # 如果文件数超过最大限制，删除最早的文件
    if len(log_files) > max_files:
        for file_to_delete in log_files[:len(log_files) - max_files]:
            os.remove(file_to_delete)
            logger.log(f"Logs Deleted: {file_to_delete}")
