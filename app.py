from flask import Flask, session, request, redirect
import route
import random
import hashlib

app = Flask(__name__)


random_key = hashlib.md5()
random_key.update(str(random.random()).encode('utf-8'))
app.secret_key = random_key.hexdigest()


# 登录中间件
def login_require(func):
    def decorator(*args, **kwargs):
        # 现在是模拟登录，获取用户名，项目开发中获取session
        try:
            username = session['status'] == True
        except:
            return redirect("login")
        # 判断用户名存在且用户名是什么的时候直接那个视图函数
        if username:
            return func(*args, **kwargs)
        else:
            # 如果没有就重定向到登录页面
            return redirect("login")

    return decorator


# @login_require
@app.route('/')
@app.route('/index')
@login_require
def index():
    uuid = request.args.get("uuid")
    return route.index(uuid)


# 登录逻辑
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        return route.login()
    else:
        return route.loginHtml()


# 注册逻辑
@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        return route.register()
    else:
        return route.registerHtml()


# 聊天逻辑

@app.route('/msg', methods=["POST"],endpoint="msg")
@login_require
def msg():
    # do something
    # print(request.form['receUser'])
    receUser = int(request.form["receUser"])
    # 确保不是自己给自己发消息
    sendUser = session['id']
    msgs = request.form["msg"]
    if msgs != "":
        route.addMsg(receUser=receUser, sendUser=sendUser, msg=msgs)
    return redirect('/index?uuid=' + str(receUser))


@app.route('/logout',endpoint="logout")
@login_require
def logout():
    return route.logout()


# 搜索用户逻辑
@app.route('/searchUser',methods=["POST"],endpoint="searchUser")
@login_require
def searchUser():
    # 通过名字搜索
    return route.searchUser()

# 添加用户逻辑
@app.route('/addUser',methods=["POST"],endpoint="addUser")
@login_require
def addUser():
    return route.addUser()


# 删除用户
@app.route('/deleteUser',methods=["POST"],endpoint="deleteUser")
@login_require
def deleteUser():
    return route.DeleteUser()

@app.route('/ChangeUser',methods=["POST"],endpoint="ChangeUser")
@login_require
def ChangeUser():
    return route.ChangeUser()

if __name__ == '__main__':
    app.run(debug=True)
