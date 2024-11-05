import os
import tempfile
import pytest
from flaskr import create_app
from flaskr.db import get_database, init_database

# 读取data.sql文件
with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    # tempfile.mkstemp()创建并打开一个临时文件，返回该文件对象和路径
    db_fd, db_path = tempfile.mkstemp()
    # 这是在测试环境，使用自定义的test_config覆盖create_app的默认配置
    # DATABASE路径被重载，这样它会指向临时路径，而不是实例文件夹
    app = create_app(test_config={
        # TESTING告诉Flask应用处在测试模式下
        # Flask会改变一些内部行为以方便测试，其他的扩展也可以使用这个标志方便测试
        'TESTING': True,
        'DATABASE': db_path,
    })
    # 设置好路径之后，创建数据库表，然后插入数据
    with app.app_context():
        init_database()
        get_database().executescript(_data_sql)

    yield app
    # 测试结束后，关闭并删除临时文件
    os.close(db_fd)
    os.unlink(db_path)


# client固件调用app.test_client()，由 app 固件创建的应用对象
# 测试会使用客户端来向应用发送请求，而不用真的启动服务器
@pytest.fixture
def client(app):
    return app.test_client()


# runner固件类似于client，app.test_cli_runner()创建一个运行器，用来调用应用注册的Click命令
# 所谓Click命令，就是用装饰器@click.command('init-db')修饰后定义的命令行命令
@pytest.fixture
def runner(app):
    return app.test_cli_runner()


# 对于大多数视图用户都需要登录才能使用
# 在测试中最方便的方法是客户端发送一个POST请求给login视图
# 与其每次都写一遍，不如写一个类，用类的方法来做这件事，并使用一个固件把它传递给每个测试的客户端
class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')

# auth固件调用类AuthActions，通过auth.login()登录为test用户
@pytest.fixture
def auth(client):
    return AuthActions(client)


