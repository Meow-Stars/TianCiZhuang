import sqlite3

import pytest
from flaskr.db import get_database


def test_get_close_db(app):
    """在一个应用环境中，每次调用get_database都应当返回相同的连接，退出后数据库连接应当已关闭"""
    with app.app_context():
        db = get_database()
        assert db is get_database()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


def test_init_db_command(runner, monkeypatch):
    """init-db命令应当调用init_database()函数并输出一个信息"""
    # 之前在db.py中用@click.command('init-db')定义了一个命令行命令init-db
    # 执行命令flask init-db，就会调用init_app()，进而调用init_db_command()，再进而调用init_database()
    # 这里使用Pytest的monkeypatch固件来替换init_database函数
    # conftest中的的runner固件用于通过名称调用init-db命令
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('flaskr.db.init_database', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert '初始化完成' in result.output
    assert Recorder.called
