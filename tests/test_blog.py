# 所有博客视图都要在已经登陆的情况下才能正常使用
# 在conftest.py里面写了个auth固件，调用auth.login()登录，并且客户端的后继请求会登录为test用户

import pytest
from flaskr.db import get_database


def test_index(client, auth):
    """测试index索引页面"""
    # index是视图1索引页面，展示所有帖子，最新的排在最前面
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data
