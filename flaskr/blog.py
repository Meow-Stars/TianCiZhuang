from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_database

# 创建一个名为blog的蓝图，然后到flaskr/__init__.py()中绑定蓝图到app实例
# blog蓝图没有像auth蓝图那样用url_prefix='/blog'，因为博客功能是主要功能，所以index视图在/，create视图在/create
bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    """视图1：索引页面，展示所有帖子，最新的排在最前面"""
    db = get_database()
    posts = db.execute(
        'SELECT p.id, title, body, created, edited, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY edited DESC'
    ).fetchall()                    # fetchall()返回一个包含所有查询结果的列表

    if posts is None:
        posts = "现在还没有求助帖哦~~~"
    # render_template()负责渲染该页面，因为是从服务器请求博客帖子数据，所以是posts
    return render_template('blog/index.html', posts=posts)


# 绑定URL到/create
@bp.route('/create', methods=('GET', 'POST'))
# 这个装饰器是在auth蓝图里自己写的，会把create视图包裹，用于检查用户登录状态
# 用户登录了那就正常访问被包裹的视图，没有登录那就重定向到登录页面
@login_required
def create():
    """视图2：创建帖子"""
    if request.method == 'POST':
        title = request.form['title']           # 帖子标题
        body = request.form['body']             # 帖子正文内容，一般是文字，允许上传图片、文件等
        money = request.form['money']           # 求助金额，必填

        error = None

        if not title:
            error = '标题为必填项！'
        if not body:
            error = '必须详细说明求助原因！'
        if not money:
            error = '求助金额为必填项！'

        if error is not None:
            flash(error)
        else:
            db = get_database()
            db.execute(
                'INSERT INTO post (title, body, author_id, money)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, g.user['id'], money)
            )
            # 调用db.commit()来保存对数据库的更新
            db.commit()
            # 帖子发布完成后重定向到索引页面
            return redirect(url_for('blog.index'))

    # render_template()负责渲染对应的HTML
    return render_template('blog/create.html')


def get_post(id, check_author=True):
    """Join post和user这两张表，把帖子和作者对上，再根据当前post_id找出唯一那一个帖子"""
    post = get_database().execute(
        'SELECT p.id, title, body, money, created, edited, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    # 如果post为None，说明这个帖子不存在
    # abort()会抛出一个特殊异常，返回一个HTTP状态码，可以自定义错误提示，也可以用默认的
    if post is None:
        abort(404, f"求助帖（id：{id}）不存在。")
    # 如果帖子的author_id≠当前登录用户的用户ID，说明该用户没有编辑和删除权限
    if check_author and post['author_id'] != g.user['id']:
        abort(403, "你不是本帖第一负责人，无法编辑该帖子。")

    return post


# 在URL中包含一个int类型的变量，这是当前帖子的post_id
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
# 编辑帖子之前一定要检查用户登录状态
@login_required
def update(id):
    """视图3：编辑帖子"""
    # 根据post_id从数据库中取出对应帖子
    post = get_post(id)

    # 这下面有一部分代码和create重合了，之后改一下
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        money = request.form['money']
        error = None

        if not title:
            error = '标题不可为空！'
        if not body:
            error = '求助原因必须详细说明！'
        if not money:
            error = '求助金额不可为空！'

        if error is not None:
            flash(error)
        else:
            db = get_database()
            db.execute(
                'UPDATE post SET title = ?, body = ?, money = ?, edited = CURRENT_TIMESTAMP'
                ' WHERE id = ?',
                (title, body, money, id)
            )
            # 将更新提交到数据库
            db.commit()
            # 重定向到博客的索引页面
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


# 删除按钮是update.html的一部分，用来发送请求到/<id>/delete，然后重定向到索引页面
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    """视图4：删除帖子"""
    get_post(id)
    db = get_database()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
