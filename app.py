"""
这个文件必须叫app.py，因为Flask默认把程序存储在app.py中，如果改了名，比如hello.py，就要在系统环境变量里设置
在终端中输入：export FLASK_APP=hello.py
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import pymysql

# 创建Flask类的实例
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:C.C.MySQL7@127.0.0.1:3306/Flask'

# 在app.config中设置好连接数据库的信息，然后使用SQLAlchemy(app)创建一个db对象
# SQLAlchemy会自动读取app.config中连接数据库的信息
db = SQLAlchemy(app)

print("MySQL数据库连接成功！")


# 在python中，带有@的是装饰器，@app.route('URL')是Flask中的装饰器，告诉Flask触发函数的URL
# 此处的URL是/，代表根路径，运行程序打开http://127.0.0.1:5000/，就会自动触发这个函数
@app.route('/')
def hello_world():
    return '<h1>Hello World!<h1>'


if __name__ == '__main__':
    app.run()

"""
项目目录将会包含：
1. flaskr/，一个包含你的应用代码和文件的 Python 包。
2. tests/，一个包含测试模块的目录。
3. venv/，一个 Python 虚拟环境文件夹，Flask 和其他依赖会被安装到这里。
4. 安装文件，用来告诉 Python 如何安装你的项目。
5. 版本控制工具的配置文件，比如 git。你应该养成为所有项目使用某类版本控制工具的习惯，不管项目大小。
6. 其他未来会添加的项目文件。
"""

# Flask应用是Flask类的实例。关于这个应用的一切，比如配置和URL，都会使用这个类注册
# 与其全局创建一个Flask类实例，不如在一个函数里创建它。这个函数被称为“应用工厂”
# 应用所需要的任何配置、注册和其他设置都将在这个函数里进行，然后应用会被返回
