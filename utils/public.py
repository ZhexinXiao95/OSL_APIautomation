def validate_params(required_params, kwargs):
    """
    公共的参数验证函数，检查kwargs中是否包含所有必需的参数。
    :param required_params: 必须的参数名列表。
    :param kwargs: 接收的关键字参数字典。
    :return: 如果所有必需的参数都在kwargs中，返回验证通过的参数字典，否则抛出异常。
    """
    missing_params = [param for param in required_params if param not in kwargs]

    if missing_params:
        raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")

    # 返回已验证的参数
    return kwargs
