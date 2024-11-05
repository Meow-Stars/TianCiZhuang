import pytest
from flask import g, session
from flaskr.db import get_database


def test_register(client, app):
    """测试register功能"""
    # register视图应当在GET请求时渲染成功，也就是返回状态码200，如果渲染失败会返回500
    # client.get()发送一个GET请求并由Flask返回Response对象
    assert client.get('/auth/register').status_code == 200
    # 在POST请求中，表单数据合法时，该视图应当保存数据到数据库，并重定向到登录URL，数据非法时，显示出错信息
    # client.post()发送一个POST请求，并把data为表单数据
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    # 当注册视图重定向到登录视图时， headers会有一个包含登录URL的Location头部
    assert 'http://localhost/auth/login' == response.headers['Location']

    with app.app_context():
        assert get_database().execute(
            "select * from user where username = 'a'",
        ).fetchone() is not None


# pytest.mark.parametrize告诉Pytest以不同的参数运行同一个测试
# 这里用于测试不同的非法输入和出错信息，避免重复写三次相同的代码。
@pytest.mark.parametrize(('username', 'password', 'message'), (
        ('', '', 'Username不可为空。'),
        ('a', '', 'Password不可为空。'),
        ('test', 'test', '用户名已存在。'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.get_data(as_text=True)


def test_login(client, auth):
    """测试login功能"""
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    # 登陆成功后应当重定向到主页视图
    assert response.headers['Location'] == 'http://localhost/'

    # 在with块中使用client，可以在响应返回之后继续操作环境变量，比如session
    # 通常，在请求之外操作session会引发一个异常
    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
        ('a', 'test', 'Username错误，用户不存在。'),
        ('test', 'a', 'Password错误。'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.get_data(as_text=True)


def test_logout(client, auth):
    """测试logout功能"""
    auth.login()

    # 注销之后，session中不应该包含user_id
    with client:
        auth.logout()
        assert 'user_id' not in session
