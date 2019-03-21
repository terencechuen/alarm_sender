import requests
import json
import time
import os

tmp_file_path = os.getcwd() + '/alarm_sender.tmp'

# 获取当前的时间戳
timestamp_now = round(time.time() * 1000)


def write_tmp(app_key, new_token):
    try:
        r_tmp = open(tmp_file_path, 'r')
    except FileNotFoundError:
        tmp_content = ''
    else:
        tmp_content = r_tmp.read()
        r_tmp.close()

    try:
        tmp_dict = json.loads(tmp_content)
    except json.decoder.JSONDecodeError:
        tmp_dict = dict()

    if "ali" in tmp_dict.keys():
        try:
            del tmp_dict["ali"][app_key]
        except KeyError:
            pass
        else:
            tmp_dict["ali"][app_key] = {"timestamp": timestamp_now, "token": new_token}
    else:
        tmp_dict["ali"] = {app_key: {"timestamp": timestamp_now, "token": new_token}}

    r_tmp = open(tmp_file_path, 'w')
    r_tmp.write(json.dumps(tmp_dict))
    r_tmp.close()


class AliDingTalk:
    def __init__(self, appkey, appsecret):
        self.appkey = appkey
        self.appsecret = appsecret

    def chk_token(self):

        # 尝试读取文件
        try:
            r = open(tmp_file_path, 'r')
        except FileNotFoundError:
            return None
        else:
            r_content = r.readline()
            r_dict = json.loads(r_content)
            r.close()

        # 尝试获取旧token
        try:
            wc_token_last = r_dict["wechat"][self.appkey]["token"]
        except KeyError:
            return None
        else:
            wc_token_timestamp_last = r_dict["wechat"][self.appkey]["timestamp"]

        # 判断有效期
        if int(timestamp_now) - int(wc_token_timestamp_last) > 6600000:
            return None
        else:
            return wc_token_last

    def get_token(self):
        url = "https://oapi.dingtalk.com/gettoken?appkey=" + self.appkey + "&appsecret=" + self.appsecret
        r = requests.get(url)
        r_content = r.content
        r_dict = json.loads(r_content)

        if r_dict["errcode"] == 0:
            write_tmp(self.appkey, r_dict["access_token"])
            return True, r_dict["access_token"]
        else:
            return False, r_dict

    @staticmethod
    def send_msg(access_token, chatid, msg_content):
        post_content = {
            "msgtype": "text",
            "text": {
                "content": msg_content
            },
            "chatid": chatid
        }
        msg_content = json.dumps(post_content, ensure_ascii=False)
        url = 'https://oapi.dingtalk.com/chat/send?access_token=' + str(access_token)
        r = requests.post(url, msg_content.encode('utf-8'), timeout=5)
        r_content = r.content.decode()

        output_content = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + ' dingding ' + r_content
        return output_content
