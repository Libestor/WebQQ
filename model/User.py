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
        self.getUidSql = "SELECT id FROM `user` WHERE username=%s"
        self.LoginSql = "SELECT * FROM login WHERE `username`=%s AND `password`=%s"
        self.RegisterUserSql = "INSERT INTO `user`(`username`, `sex`,`email`) VALUES (%s, %s,%s)"
        self.RegisterLoginSql = "INSERT INTO `login`(`username`, `password`) VALUES (%s, %s)"
        self.CheckRegisterVaildSql = "SELECT * FROM user WHERE `username`=%s"
        self.CheckUserSql = "SELECT * FROM `user` WHERE `id`=%s"
        self.CheckFriendSql = "SELECT * FROM `relation` WHERE (`user1`=%s AND `user2`=%s) OR (`user2`=%s AND `user1`=%s)"
        self.AddUserSql = "INSERT INTO `relation`(`user1`, `user2`) VALUES(%s,%s)"
        self.DeleteUserSql = "DELETE FROM `relation` WHERE (`user1` = %s AND user2 = %s )OR (`user2` = %s AND `user1` = %s);"
        self.GetFriendsSql = "SELECT id,username,sex FROM `user` WHERE `id` IN (SELECT user1 FROM `relation` WHERE `user2`=%s UNION " \
                             "SELECT user2 FROM `relation` WHERE `user1`=%s)"

    def __del__(self):
        self.db.close()

    def getUid(self, name: str):
        cursor = self.db.cursor()
        res = cursor.execute(self.getUidSql, (name,))
        if res == 0:
            return False
        id = cursor.fetchone()[0]
        return id

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

    def sqlInject(self, s: str):
        if '\'' in s or '\"' in s:
            return False
        else:
            return True

    # 密码的hash计算
    def GetpassMd5(self, passwd):
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
            passMd5 = self.GetpassMd5(password)
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
        passMd5 = self.GetpassMd5(passwd)
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
        userid = self.getUid(username)

    # 查询是否存在用户
    def CheckUser(self, uid):
        curcor = self.db.cursor()
        res = curcor.execute(self.CheckUserSql, (uid,))
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
        if self.CheckFriend(uid1,uid2):
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
            tmp = {}
            for friend in allFriend:
                tmp["id"] = friend[0]
                tmp["name"] = friend[1]
                tmp["sex"] = friend[2]
                friends.append(tmp.copy())
        else:
            return False
        return friends


if __name__ == "__main__":
    mysql = User()

