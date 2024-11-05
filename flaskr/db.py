from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()

import re
import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext
"""g是全局上下文，是一个特殊的对象，它对每一个请求都是唯一的，用来存储在处理请求时可能会被多个函数访问的数据
   如果get_database在同一个请求中被二次调用，该连接会被存储和复用，而不是创建一个新的连接
   current_app是另一个特殊的对象，它指向处理请求的Flask应用
   因为使用了应用工厂flaskr，所以当写其他部分代码时没有应用对象，当应用处理请求时get_database被调用"""

def get_database():
    if 'db' not in g:
        # 建立一个连接到配置键DATABASE指向的文件。这个文件还不存在，初始化数据库才会被创建。
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # sqlite3.Row表示查询结果的返回类型为字典，这样可以通过属性名访问列
        g.db.row_factory = sqlite3.Row

        # 初始化MySQL，SQLAlchemy会自动读取app.config中连接数据库的信息
        # g.db = SQLAlchemy()

    return g.db


# 关闭数据库连接
def close_database(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


# 初始化数据库，
def init_database():
    # get_database()返回一个数据库连接，用来执行从文件中读取的命
    db = get_database()
    # open_resource()打开一个相对于flaskr文件夹的文件
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# 装饰器click.command()定义了一个名为init-db的命令行命令
# 在终端执行这个命令flask init-db会调用init_database()函数并向用户显示一个成功消息
@click.command('init-db')
@with_appcontext
def init_db_command():
    """清除现有数据，并创建新的表"""
    init_database()
    # 输出文本Initialized the database.
    click.echo('数据库初始化完成。')


"""close_database()和init_db_command()需要被注册到Flask实例，也就是app，否则用不了"""
# 将函数注册到应用，然后到__init__.py的create_app()中调用init_app()
def init_app(app):
    # 告诉Flask在返回响应以后，调用该函数关闭数据库
    app.teardown_appcontext(close_database)
    # 添加一个新的命令，可以使用flask命令调用
    app.cli.add_command(init_db_command)
