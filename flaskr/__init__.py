# __init__.py有两个作用：它将包含应用工厂，而且告诉Python，flaskr目录应该被看做一个包
import os
from flask import Flask


def create_app(test_config=None):
    """创建Flask类的实例，换而言之，这个函数create_app就是个应用工厂"""
    # __name__是当前Python模块的名称，instance_relative_config=True告诉app配置文件的位置是相对于实例文件夹
    app = Flask(__name__, instance_relative_config=True, template_folder='../templates')
    # 一些app的默认配置
    app.config.from_mapping(
        # 用于保持数据安全，在开发时写成dev，部署时应该用一个随机值覆盖
        SECRET_KEY='dev',
        # 保存SQLite数据库文件的路径
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),

        # MySQL数据库配置信息
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:C.C.MySQL7@127.0.0.1:3306/Flask',
        # 是否追踪数据库修改，一般不开启, 会影响性能
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
        # # 是否显示底层执行的SQL语句
        # SQLALCHEMY_ECHO = True
    )

    if test_config is None:
        # 如果存在文件config.py，会用其中的设置覆盖上面的默认配置，例如部署时的SECRET_KEY
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 如果有单独的test_config，这是独立的测试配置，用于测试环境
        app.config.from_mapping(test_config)

    # 确保实例文件夹存在，因为Flask不会在路径不存在时自动创建，只能显式创建
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    """装饰器，打开http://127.0.0.1:5000/hello就会自动执行被该装饰器修饰的函数"""
    # 一般这个指向首页
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # 从当前目录下导入文件db，调用函数init_app(app)
    # 因为在db.py中用@click.command('init-db')定义了一个命令行命令init-db
    # 执行命令flask init-db，就会调用init_app()，进而调用init_db_command()
    # 创建好数据库后，会在instance文件夹中出现一个名为flaskr.sqlite的文件
    from . import db
    db.init_app(app)

    """绑定用户认证蓝图，负责实现注册、登录、登出、用户登录状态管理"""
    from . import auth
    app.register_blueprint(auth.bp)

    """绑定博客蓝图，展示所有帖子，登录用户可以创建、浏览帖子，帖子的作者可以编辑或者删除"""
    from . import blog
    app.register_blueprint(blog.bp)
    # app.add_url_rule将端点名index和路径/绑定到一起，这样url_for('index')就不会生成错误路径
    app.add_url_rule('/', endpoint='index')

    return app

# 该项目在Github上的地址：https://github.com/Meow-Stars/TianCiZhuang.git
# git@github.com:Meow-Stars/TianCiZhuang.git
