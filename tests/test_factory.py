from flaskr import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_hello(client):
    """测试路径/hello，通过断言判断返回结果是否是'Hello, World!'，是则通过测试"""
    response = client.get('/hello')
    assert response.data == b'Hello, World!'
