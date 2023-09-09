import pymysql
import config
import time
import datetime


def escape_quotes(value):
    # 转义单引号
    value = value.replace("'", "\\'")
    # 转义双引号
    value = value.replace('"', '\\"')
    return value


def GetTimeHM(timestamp):
    dt = datetime.datetime.fromtimestamp(int(timestamp))
    # 格式化为指定的格式：20:30
    time_format = dt.strftime('%H:%M')
    return time_format


class Message:
    def __init__(self):
        self.db = pymysql.connect(
            host=config.DataBase.get("host"),
            port=config.DataBase.get("port"),
            user=config.DataBase.get("username"),
            password=config.DataBase.get("password"),
            database=config.DataBase.get("database")
        )

        # 添加数据的sql语句
        self.LoginSql = "SELECT * FROM login WHERE `username`=%s AND `password`=%s"
        self.RegisterUserSql = "INSERT INTO `user`(`username`, `sex`,`email`) VALUES (%s, %s,%s)"
        self.RegisterLoginSql = "INSERT INTO `login`(`username`, `password`) VALUES (%s, %s)"
        self.CheckRegisterVaildSql = "SELECT * FROM user WHERE `username`=%s"
        self.getUidsql = "SELECT id FROM user WHERE username=%s"
        self.getNameSql = "SELECT username From user WHERE id=%s"
        self.getSexSql = "SELECT sex FROM user WHERE id=%s"
        self.AddmsgSql = "INSERT INTO `message`(`senduser`,`receiveuser`,`msg`,`time`) VALUES(%s,%s,%s,%s)"
        self.GetMessageSql = "SELECT senduser,receiveuser,msg,time FROM `message` WHERE " \
                             "(senduser=%s AND receiveuser=%s) OR (receiveuser=%s AND senduser=%s) ORDER BY time"

    def __del__(self):
        self.db.close()

    def getUid(self, name: str):
        cursor = self.db.cursor()
        res = cursor.execute(self.getUidsql, (name,))
        if res == 0:
            return False
        id = cursor.fetchone()[0]
        return id

    def Addmsg(self, sendUser: int, receUser: int, msg: str):
        # 获取当前时间

        nowTime = int(time.time())
        msg = escape_quotes(msg)
        cursor = self.db.cursor()
        cursor.execute(self.AddmsgSql, (sendUser, receUser, msg, nowTime))
        self.db.commit()
        cursor.close()

    def GetSex(self, idnum):
        cursor = self.db.cursor()
        cursor.execute(self.getSexSql, (idnum,))
        sex = cursor.fetchone()
        cursor.close()
        return sex[0]

    def GetName(self, idnum):
        cursor = self.db.cursor()
        cursor.execute(self.getNameSql, (idnum,))
        name = cursor.fetchone()
        cursor.close()
        return name[0]

    def GetMessage(self, myid: int, uid: int):
        # 获取消息
        cursor = self.db.cursor()
        res = cursor.execute(self.GetMessageSql, (myid, uid, myid, uid))
        # 格式类似为
        if res != 0:
            # 消息格式化
            allmessage = cursor.fetchall()
            print("所有消息：",allmessage)
            msg = []
            for message in allmessage:
                tmp = {}
                # 如果是我发送的消息
                if message[0] == myid:
                    tmp["type"] = "self"
                    tmp["name"] = self.GetName(myid)
                    tmp["sex"] = self.GetSex(myid)
                    tmp["msg"] = message[2]
                    tmp["time"] = GetTimeHM(message[3])
                else:
                    tmp["type"] = "other"
                    tmp["name"] = self.GetName(uid)
                    tmp["sex"] = self.GetSex(uid)
                    tmp["msg"] = message[2]
                    tmp["time"] = GetTimeHM(message[3])
                msg.append(tmp.copy())
            # 消息返回
            return msg
        else:
            return False
