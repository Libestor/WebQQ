from flask import render_template, session, redirect, request
import re

from model import User, Message


def render_template_index(own=None, friends=None, msg=None, currentFriend=None):
    if own is None:
        own = {"name": "lh", "sex": 1}
    if friends is None:
        friends = [{"name": "chr", 'id': 2, "sex": 2}]
    if msg is None:
        msg = [{"name": "ypy", "sex": 2, "msg": "我今天肯定不歪", "time": "18:00", "type": "self"}
            , {"name": "lfy", "sex": 2, "msg": "上号！", "time": "18:01", "type": "other"}]
    if currentFriend is None:
        currentFriend = {"name": "chr", "id": 2}
    return render_template("index.html", own=own, friends=friends, users=msg, currentFriend=currentFriend)


def index(uuid=None, other=None, msg=None):
    # print(uuid)
    userI = User.User()
    msgI = Message.Message()
    myid = session["id"]
    friends = userI.GetFriends(myid)
    currentFriend = {}
    print("index:myid：", myid)
    if friends is False:
        friends = []
    if uuid is None:
        message = []
        uuid = []
    else:
        message = msgI.GetMessage(myid, uuid)
        if message is False:
            message = []
        # 设置currentFriend 到uuid上
        # 需要检测当前是否是好友关系：
        if userI.CheckFriend(myid, uuid):
            currentFriend = {"name": msgI.GetName(uuid), "id": uuid}
        else:
            currentFriend = []
    sex = msgI.GetSex(myid)
    own = {"name": session["username"], "sex": sex, "id": myid}
    # print(uuid)
    # print(friends)
    # print(own)
    # print(message)

    if other:
        print("other is ",other)
        print("msg is  ",msg)
        return render_template("index.html", friends=friends, own=own, msg=message, currentFriend=currentFriend,
                               other=True, alertmsg=msg)

    # print(friends)
    return render_template_index(friends=friends, own=own, msg=message, currentFriend=currentFriend)


def loginHtml():
    return render_template("login.html", registerSuccess=False)


def login():
    username = request.form['username']
    password = request.form['password']
    # 此处是登录逻辑
    user = User.User()
    if user.CheckLogin(username=username, passwd=password):
        session['username'] = username
        session['status'] = True
        uid = user.getUid(username)
        print("login：getuid",uid)
        session["id"] = uid
        return redirect("/index")
    else:
        return render_template("login.html", LoginSuccess=False)


def logout():
    # try:
    #     session['status'] = False
    #     return render_template("login.html",LogoutSuccess=True)
    # except:
    session.clear()
    return render_template("login.html", LogoutSuccess=True)


# 检测邮箱
def check_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True
    return False


def register():
    username = request.form["username"]
    password = request.form["password"]
    re_password = request.form["re_password"]
    email = request.form["email"]
    sex = request.form['sex']
    # 两次密码不正确,此处可以增加更多的返回内容
    if password != re_password or not check_email(email):
        return render_template("register.html", registerSuccess=False)

    if sex == "男":
        sex = 2
    elif sex == '女':
        sex = 1
    else:
        return render_template("register.html", registerSuccess=False)
    # 开始注册
    user = User.User()
    # 检测是否用户名唯一
    if user.CheckRegisterVaild(username=username):
        # 开始录入
        if user.RegisterUser(username=username, password=password, sex=sex, email=email):
            return render_template("login.html", registerSuccess=True)
        else:
            return render_template("register.html", registerSuccess=False)
    else:
        return render_template("register.html", UserNotOnly=True)


def registerHtml():
    return render_template("register.html")


def addMsg(receUser: int, sendUser: int, msg: str):
    message = Message.Message()
    message.Addmsg(receUser=receUser, sendUser=sendUser, msg=msg)


# 呈现好友
def GetFriends():
    # 获得用户
    user = User.User()
    Friend = user.GetFriends()
    return Friend


# 呈现用户消息
def GetMessages(Uid):
    # 获得消息
    messageI = Message.Message()
    message = messageI.GetMessage(int(Uid))
    return message


# 搜索用户
def searchUser():
    name = request.args.get("name")
    userI = User.User()
    users = userI.SearchUser(name)
    print("搜索结果：", users)
    myid = session["id"]
    sex = userI.GetSex(myid)
    own = {"name": session["username"], "sex": sex, "id": myid}
    return render_template("index.html", own=own, friends=users, msg=[], currentFriend={})


# 添加用户为好友
def addUser():
    AddUserId = request.form["Id"]
    selfId = session['id']
    user = User.User()
    res = user.AddUser(int(selfId), int(AddUserId))
    if res is True:
        return index(other=True, msg="添加成功")
    else:
        return index(other=True, msg="添加失败")


def ChangeUser():
    username = request.form["username"]
    sex = request.form["sex"]
    print("change: sex: ",sex)
    if sex == "男":
        sex = 2
    elif sex == "女":
        sex = 1
    else:
        sex = 0
    print("change: final sex",sex)

    myid = int(session["id"])
    passwd = request.form["oldPassword"]
    newPasswd = request.form["newPassword"]
    reNewPasswd = request.form["reNewPassword"]
    # 修改密码
    user = User.User()
    if sex != 0:
        user.ChangeSex(myid=myid,sex=sex)
    if username != "":
        if not user.ChangeUsername(myid=myid,username=username):
            print("用户名修改失败")
            return render_template("login.html",other=True,alertmsg="用户名修改失败")
    if newPasswd != reNewPasswd:
        return render_template("login.html",other=True,alertmsg="两次密码不正确")
    if newPasswd != "":
        res = user.ChangePasswd(myid=myid, old=passwd, new=newPasswd)
        if res == "OldFalse":
            print("OldFalse")
            return render_template("login.html",other=True,alertmsg="旧密码不正确")
        elif res is False:
            print("修改失败")
            return index(other=True, msg="修改失败")

    session.clear()
    return render_template("login.html",other=True,alertmsg="信息修改成功，请重新登录")


def DeleteUser():
    DelteUserId = int(request.form["Id"])
    selfId = int(session["id"])
    user = User.User()
    res = user.DeleteUser(DelteUserId, selfId)
    if res:
        return index(other=True, msg="删除成功")
    else:
        return index(other=True, msg="删除失败")
