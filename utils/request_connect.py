import copy
import time
import json
import base64
import hashlib
import hmac
import requests
import uuid

from utils.ini_read import *
from utils.log import logger
env = read_pytest_ini('env', 'global setting')
base_url = read_pytest_ini('api_host', env)
key = read_pytest_ini('api_key', env)
secret = read_pytest_ini('api_secret', env)


def generate_traceid():
    traceid = str(uuid.uuid4())
    return traceid


def gen_sig_helper(secret, data):
    secret_bytes = base64.b64decode(secret.encode("utf8"))
    result = base64.b64encode(hmac.new(secret_bytes, data.encode("utf8"), digestmod=hashlib.sha512).digest()).decode(
        "utf8")
    return result


def v3_gen_sig(secret, path, body_str=None):
    data = path
    if body_str != None:
        data = data + chr(0) + body_str
    return gen_sig_helper(secret, data)


def v4_gen_sig(secret, method, path, expires, body_str=None):
    data = method + path + str(expires)
    if body_str is not None:
        data = data + body_str
    return gen_sig_helper(secret, data)


def v3_mk_request(method, path, dict={}, trace_id=None, log=True):
    tonce = int(time.time() * 1000 * 1000)
    body = copy.deepcopy(dict)
    body["tonce"] = tonce
    case_title = ''
    body_str = json.dumps(body)
    headers = {
        "Rest-Key": key,
        "Rest-Sign": v3_gen_sig(secret, path, body_str),
        "Content-Type": "application/json"
    }
    response = requests.request(method, base_url + "/" + path, headers=headers, data=body_str)
    try:
        if log:
            logger.log(f"Request> [{trace_id}] => " + method + ' ' + path + ' <Param> => ' + str(body))
            logger.log(f'<Response> [{trace_id}] => {response.json()}')
        response.raise_for_status()
        assert response.json()
        request_msg = f"<Request> [{trace_id}] => " + method + ' ' + path + ' <Param> => ' + str(body)
        response_msg = f'<Response> [{trace_id}] => {response.json()}'
        response_json = response.json()
        dict = {'response': response, 'res': response_json, 'req_msg': request_msg, 'res_msg': response_msg}
        return dict

    except Exception as ex:
        logger.log(f"<{case_title} v3_mk_request unknow error {str(ex)}", 'critical')
        raise ex


def v4_mk_request(method, path, body=None, log=True, need_res=True):
    tonce = int(time.time()) + 10
    body_str = None
    if body:
        body_str = json.dumps(body)
    headers = {
        'api-key': key,
        'api-signature': v4_gen_sig(secret, method, path, tonce, body_str),
        'api-expires': str(tonce),
    }
    if body:
        headers['Content-Type'] = 'application/json'

    response = requests.request(method, base_url + path, headers=headers, data=body_str)

    try:
        if need_res:
            if log:
                logger.log(f"Request> => " + method + ' ' + path + ' <Param> => ' + str(body))
                logger.log(f'<Response> => {response.json()}')
            # response.raise_for_status()
            # assert response.json()
            request_msg = f"<Request> => " + method + ' ' + path + ' <Param> => ' + str(body)
            response_msg = f'<Response> => {response.json()}'
            response_json = response.json()
            dict = {'response': response, 'res': response_json, 'req_msg': request_msg, 'res_msg': response_msg}
            return dict
        else:
            return response

    except Exception as ex:
        logger.log(f"v4_mk_request unknow error {str(ex)}", 'critical')
        raise ex


def make_request(method, path, headers, params=None, timeout=5):
    try:
        if method.upper() == 'GET':
            response = requests.get(path, headers=headers, params=params, timeout=timeout)
            logger.log(f"请求url: {response.url}\n响应体: {response.text}", 'debug')
        elif method.upper() == 'POST':
            response = requests.post(path, headers=headers, json=params, timeout=timeout)
            logger.log(f"请求url: {response.url}\n请求体: {response.request.body.decode('utf-8')}\n响应体: {response.text}", 'debug')
        else:
            raise ValueError(f"make_request Unsupported HTTP method: {method}")
        response.raise_for_status()  # 如果请求不成功，抛出异常
        assert response.status_code == 200, f'make_request api request receive {response.status_code}, Request: {response.request.body}'
        assert response.json()
        # 根据 Content-Type 处理不同类型的响应
        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/json' in content_type:
            return response.json()
        elif 'text/' in content_type:
            return response.text
        elif 'image/' in content_type:
            return response.content  # 返回二进制数据
        else:
            return response.json()  # 默认返回文本

    except requests.exceptions.RequestException as e:
        logger.log(f"{path} An error occurred: {e}", "error")
        raise e

if __name__ == '__main__':
    v4_mk_request('DELETE','/api/v4/order/all')