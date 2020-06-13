# __author = wulinjun
# date:2020/6/2 23:57


import hashlib


def set_pwd(values):
    """

    :param values: 需要被加密的数据
    :return:
    """
    secret_key = "strangebee".encode('utf-8')
    md5_value = hashlib.md5(secret_key)
    md5_value.update(values.encode('utf-8'))
    return md5_value.hexdigest()




