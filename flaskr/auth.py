import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_database


# 创建一个名为auth的蓝图，url_prefix将会被添加到所有和这个蓝图相关的URL前
# 然后到flaskr/__init__.py()中绑定蓝图到app实例
bp = Blueprint('auth', __name__, url_prefix='/auth')


"""视图1：注册"""
@bp.route('/register', methods=('GET', 'POST'))
# 因为前面创建蓝图的使用用了url_prefix='/auth'，会自动把/auth添加到和这个蓝图有关的URL前面
# 所以/register不存在，而当用户访问/auth/register时，register视图会返回HTML，其中包含一个让他们填写的表单
# 当用户提交表单时，会验证他们的输入，然后要么再次显示表单和一个错误消息，要么创建新用户并跳转到登录页面
# 把/register关联到register视图函数，当用户访问/auth/register时，自动调用register视图函数并使用返回值作为响应
def register():
    # 如果用户提交了表单，request.method会是POST，视图开始验证输入的数据
    if request.method == 'POST':
        # request.form是一个特殊类型的dict，它映射用户提交的表单键（元素id）到相应的值
        username = request.form['username']
        password = request.form['password']
        # database中用的是g，同一个请求被二次调用时会复用原来的连接，而不是创建一个新连接
        db = get_database()

        error = None
        # 首先验证username和password不能为空
        if not username:
            error = 'Username不可为空。'
        elif not password:
            error = 'Password不可为空。'
        # 基本验证通过后，将新用户插入到数据库中
        if error is None:
            try:
                # db.execute()会接收一个SQL语句，其中包含一个用于用户输入的占位符，以及一个用于替换占位符的数值元组
                # 数据库库会对这些值进行转义处理，因此不会受到SQL注入攻击
                # 密码不应该明文存储，所以用generate_password_hash(password)对密码进行加密
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                # 由于INSERT会更改数据库，所以调用db.commit()来保存更改
                db.commit()
            # except用于捕获异常
            # 如果用户名已存在，则会出现sqlite3.IntegrityError，这作为另一个验证错误显示给用户
            except db.IntegrityError:
                error = f"用户名已存在。"
            # 只有没有捕获到异常，才会执行else代码块
            # 新用户插入到user表后，被重定向到login视图。url_for("auth.login")会根据名称自动生成到login视图的URL
            # 这样以后可以随意修改login视图对应的URL，不需要一个个更新链接到它的URL
            # redirect()生成一个重定向URL，指向login页面
            else:
                return redirect(url_for("auth.login"))

        # 如果验证失败，error不为None，flash(error)存储错误信息，可以被页面渲染捕获，展示给用户
        flash(error)

    # 当用户访问auth/register时，应该显示对应的HTML，render_template()负责渲染该页面
    return render_template('auth/register.html')


"""视图2：登录"""
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None
        # 执行SQL语句
        # fetchone()从查询中返回一条记录，如果查询没有返回结果，则返回None
        # 另一个效果类似的函数叫fetchall()，返回一个包含所有查询结果的列表
        user = get_database().execute(
            'SELECT username, password FROM user WHERE username = ?', (username,)
        ).fetchone()

        # 如果fetchone()返回None，说明该用户名不在数据库内，所以用户名不正确
        if user is None:
            error = 'Username错误。'
        # 注册时用generate_password_hash(password)对密码进行加密
        # check_password_hash(A, B)对用户输入的密码B进行加密，然后和数据库中存储的密码A进行对比
        # 如果匹配就是密码正确
        elif not check_password_hash(user['password'], password):
            error = 'Password错误。'

        if error is None:
            """验证成功后，用户id被存储到一个新的session，session是一个dict，存储在服务器上，用来存储跨请求的数据
               数据被存储到一个发送给浏览器的cookie中，浏览器会在后续的请求中把它发送回来
               Flask对数据进行安全签名，使其无法被篡改"""
            # 用户id被存储在服务器的session中，在后续请求中，如果用户已经登录，其他视图可以加载session中的信息
            session.clear()
            session['user_id'] = user['id']
            # 重定向到index视图，这个视图在blog蓝图里面，指向index()视图函数
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


"""注册一个函数并让它在每一个视图函数之前运行
   这样不管请求发到哪一个URL，load_logged_in_user()都会检查用户ID是否存储在session中
   在session中就是用户处于登录状态，于是从数据库中获取对应用户的数据，存储到g.user上
   g存在于单个请求的生命周期内，如果没有用户ID不存在，g.user=None"""
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_database().execute(
            'SELECT username, password FROM user WHERE id = ?', (user_id,)
        ).fetchone()


"""视图3：登出，也就是从session中移除对应的用户ID"""
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


"""无论是浏览、创建、编辑、删除帖子都需要用户处于登录状态，所以使用一个装饰器@functools.wraps(view)
   将函数login_required(view)变成一个装饰器，为每个使用它的视图检查登录状态"""
# 这个装饰器会包裹被它修饰的视图函数，检查用户的登录状态，登录了则会调用原视图继续正常运行，否则重定向到登录页面
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
