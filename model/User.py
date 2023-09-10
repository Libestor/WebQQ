# -*- coding:utf-8 -*-

import pymysql
import config
import hashlib


class User:

    def __init__(self):

        self.db = pymysql.connect(
            host=config.DataBase.get("host"),
            port=config.DataBase.get("port"),
            user=config.DataBase.get("username"),
            password=config.DataBase.get("password"),
            database=config.DataBase.get("database")
        )

        # 添加数据的sql语句
        self.getUsernameSql = "SELECT username FROM `user` WHERE id=%s"
        self.getUidSql = "SELECT id FROM `user` WHERE username=%s"
        self.LoginSql = "SELECT * FROM `login` WHERE `username`=%s AND `password`=%s"
        self.RegisterUserSql = "INSERT INTO `user`(`username`, `sex`,`email`) VALUES (%s, %s,%s)"
        self.RegisterLoginSql = "INSERT INTO `login`(`username`, `password`) VALUES (%s, %s)"
        self.CheckRegisterVaildSql = "SELECT * FROM user WHERE `username`=%s"
        self.CheckUserSql = "SELECT * FROM `user` WHERE `id`=%s"
        self.getSexSql = "SELECT sex FROM user WHERE id=%s"
        self.CheckFriendSql = "SELECT * FROM `relation` WHERE (`user1`=%s AND `user2`=%s) OR (`user2`=%s AND " \
                              "`user1`=%s)"
        self.AddUserSql = "INSERT INTO `relation`(`user1`, `user2`) VALUES(%s,%s)"
        self.DeleteUserSql = "DELETE FROM `relation` WHERE (`user1` = %s AND user2 = %s )OR (`user2` = %s AND `user1` = %s);"
        self.GetFriendsSql = "SELECT id,username,sex FROM `user` WHERE `id` IN (SELECT user1 FROM `relation` WHERE `user2`=%s UNION " \
                             "SELECT user2 FROM `relation` WHERE `user1`=%s)"
        self.SearchUserSql = "SELECT id,username,sex FROM `user` WHERE username LIKE %s"
        self.CheckUsernameSql = "SELECT * FROM `user` WHERE username=%s"
        self.UpdateUsernameSql = "UPDATE `user` SET username = %s WHERE id = %s"
        self.UpdateSexSql = "UPDATE `user` SET sex = %s WHERE id = %s"
        self.UpdateLoginUsernameSql = "UPDATE `login` SET username = %s WHERE username = %s"
        self.UpdatePasswordSql = "UPDATE `login` SET `password` = %s WHERE username = %s"

    def __del__(self):
        self.db.close()

    def getUid(self, name: str):
        cursor = self.db.cursor()
        res = cursor.execute(self.getUidSql, (name,))
        if res == 0:
            return False
        id = cursor.fetchone()[0]
        return id

    def GetSex(self, idnum: int):
        cursor = self.db.cursor()
        cursor.execute(self.getSexSql, (idnum,))
        sex = cursor.fetchone()
        cursor.close()
        return sex[0]

    def is_connected(self):
        """Check if the server is alive"""
        try:
            self.db.ping(reconnect=True)
        except:
            self.db = pymysql.connect(
                host=config.DataBase.get("host"),
                port=config.DataBase.get("port"),
                user=config.DataBase.get("username"),
                password=config.DataBase.get("password"),
                database=config.DataBase.get("database")
            )

    # 返回True就表示可以正常使用
    def sqlInject(self, s: str):
        if '\'' in s or '\"' in s:
            return False
        else:
            return True

    # 密码的hash计算
    def getpassMd5(self, passwd):
        passMd5 = hashlib.md5()
        passMd5.update(passwd.encode("utf-8"))
        return passMd5.hexdigest()

    # 性别默认1是女，2是男
    def RegisterUser(self, username, password, sex, email):
        if self.sqlInject(username) and self.sqlInject(email):
            # 在主表中加入数据
            self.is_connected()
            cursor = self.db.cursor()
            cursor.execute(self.RegisterUserSql, (username, sex, email))
            # 在登录表中加入数据
            passMd5 = self.getpassMd5(password)
            cursor.execute(self.RegisterLoginSql, (username, passMd5))

            self.db.commit()
            cursor.close()
            return True
        else:
            return False

    def CheckRegisterVaild(self, username):
        if self.sqlInject(username):
            self.is_connected()
            cursor = self.db.cursor()
            res = cursor.execute(self.CheckRegisterVaildSql, username)
            if res != 0:
                return False
            else:
                return True
        else:
            return False

    def CheckLogin(self, username, passwd):
        passMd5 = self.getpassMd5(passwd)
        # 进行sql关键字过滤：
        if self.sqlInject(username):
            # 进行预编译：
            cursor = self.db.cursor()
            res = cursor.execute(self.LoginSql, (username, passMd5))
            if res == 1:
                return True
            else:
                return False
        else:
            return False

    # 检查是否是好友关系
    def CheckFriend(self, myid, uid):
        cursor = self.db.cursor()
        res = cursor.execute(self.CheckFriendSql, (myid, uid, myid, uid))
        cursor.close()
        if res != 0:
            return True
        else:
            return False

    # 按照名字查询
    def SearchUser(self, username: str):
        # 确保sql特殊字符过滤成功
        if self.sqlInject(username):
            cursor = self.db.cursor()
            res = cursor.execute(self.SearchUserSql, (username + "%",))
            print("搜索好友查询数量: ", res)
            friends = []
            if res != 0:
                allUser = cursor.fetchall()
                cursor.close()
                for user in allUser:
                    friends.append({"name": user[1], 'id': user[0], "sex": user[2]})
                return friends
            else:
                return []
        else:
            return []

    # 查询是否存在用户
    def CheckUser(self, uid: int):
        cursor = self.db.cursor()
        res = cursor.execute(self.CheckUserSql, (uid,))
        cursor.close()
        if res == 0:
            return False
        else:
            return True

    def AddUser(self, myid: int, uid: int):
        if self.CheckUser(uid):
            cursor = self.db.cursor()
            cursor.execute(self.AddUserSql, (myid, uid))
            self.db.commit()
            cursor.close()
            return True
        else:
            return False

    def DeleteUser(self, uid1, uid2):
        if self.CheckFriend(uid1, uid2):
            cursor = self.db.cursor()
            cursor.execute(self.DeleteUserSql, (uid1, uid2, uid1, uid2))
            self.db.commit()
            cursor.close()
            return True
        else:
            return False

    def GetFriends(self, myid: int):
        cursor = self.db.cursor()
        res = cursor.execute(self.GetFriendsSql, (myid, myid))
        friends = []
        if res != 0:
            allFriend = cursor.fetchall()
            cursor.close()
            tmp = {}
            for friend in allFriend:
                tmp["id"] = friend[0]
                tmp["name"] = friend[1]
                tmp["sex"] = friend[2]
                friends.append(tmp.copy())
        else:
            return False
        return friends

    # 检测username是否存在和合法
    def CheckUsername(self, username):
        # sql注入检测
        if self.sqlInject(username):
            cursor = self.db.cursor()
            res = cursor.execute(self.CheckUsernameSql, (username,))
            cursor.close()
            if res == 0:
                # True表示检测通过，该用户名可用
                return True
            else:
                return False
        else:
            return False

    # 修改用户名
    def ChangeUsername(self, myid: int, username):
        # 检查是否合法
        if not self.CheckUsername(username):
            return False
        cursor = self.db.cursor()
        oldName = self.GetUsername(myid)
        # 修改总表
        cursor.execute(self.UpdateUsernameSql, (username, myid))
        # 修改登录表
        cursor.execute(self.UpdateLoginUsernameSql, (username, oldName))
        self.db.commit()
        cursor.close()
        return True

    # 修改性别
    def ChangeSex(self, sex: int, myid: int):
        # 检查是否合法
        cursor = self.db.cursor()
        cursor.execute(self.UpdateSexSql, (sex, myid))
        self.db.commit()
        cursor.close()

    def GetUsername(self, myid: int):
        cursor = self.db.cursor()
        res = cursor.execute(self.getUsernameSql, (myid,))
        if res == 0:
            return False
        name = cursor.fetchone()[0]
        cursor.close()
        return name

    # 修改密码
    def ChangePasswd(self, myid: int, old, new):
        name = self.GetUsername(myid)
        # sql检测
        if not self.sqlInject(old) or not self.sqlInject(new):
            return False
        # 验证旧密码
        if not self.CheckLogin(username=name, passwd=old):
            return "OldFalse"
        # 修改密码
        username = self.GetUsername(myid)
        passMd5 = self.getpassMd5(new)
        cursor = self.db.cursor()
        cursor.execute(self.UpdatePasswordSql, (passMd5, username))
        self.db.commit()
        cursor.close()
        return True


if __name__ == "__main__":
    mysql = User()
