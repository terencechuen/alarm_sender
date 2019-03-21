import os
import time
import requests
import json

tmp_file_path = os.getcwd() + '/alarm_sender.tmp'

# 获取当前的时间戳
timestamp_now = round(time.time() * 1000)


def write_tmp(corp_id, new_token):
    r_tmp = open(tmp_file_path, 'r')
    tmp_content = r_tmp.read()
    r_tmp.close()

    try:
        tmp_dict = json.loads(tmp_content)
    except json.decoder.JSONDecodeError:
        tmp_dict = dict()

    if "wechat" in tmp_dict.keys():
        try:
            del tmp_dict["wechat"][corp_id]
        except KeyError:
            pass
        else:
            tmp_dict["wechat"][corp_id] = {"timestamp": timestamp_now, "token": new_token}
    else:
        tmp_dict["wechat"] = {corp_id: {"timestamp": timestamp_now, "token": new_token}}

    r_tmp = open(tmp_file_path, 'w')
    r_tmp.write(json.dumps(tmp_dict))
    r_tmp.close()


class EnterpriseWeChat:
    def __init__(self, corp_id, corp_secret, division_id, app_id):
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.division_id = division_id
        self.app_id = app_id

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
            wc_token_last = r_dict["wechat"][self.corp_id]["token"]
        except KeyError:
            return None
        else:
            wc_token_timestamp_last = r_dict["wechat"][self.corp_id]["timestamp"]

        # 判断有效期
        if int(timestamp_now) - int(wc_token_timestamp_last) > 6600000:
            return None
        else:
            return wc_token_last

    def get_token(self):
        get_access_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' \
                               + self.corp_id + '&corpsecret=' + self.corp_secret
        r = requests.get(get_access_token_url, timeout=5)
        r_content = r.content.decode()
        r_content_dict = eval(r_content)
        errmsg = r_content_dict['errmsg']

        if errmsg == "ok":
            new_token = r_content_dict['access_token']
            write_tmp(self.corp_id, new_token)
            return True, new_token
        else:
            return False, r_content_dict['errmsg']

    def send_msg(self, access_token, msg_content):
        post_content = {
            "text": {
                "content": msg_content
            },
            "toparty": self.division_id,
            "msgtype": "text",
            "agentid": self.app_id
        }
        msg_content = json.dumps(post_content, ensure_ascii=False)
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + str(access_token)
        r = requests.post(url, msg_content.encode('utf-8'), timeout=5)
        r_content = r.content.decode()

        output_content = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + ' wechat ' + r_content
        return output_content

    # DEBUG之用
    # 获取所有部门
    @staticmethod
    def get_division(access_token):
        get_wc_division = 'https://qyapi.weixin.qq.com/cgi-bin/department/list?access_token=' + str(access_token)
        r = requests.get(get_wc_division, timeout=5)
        r_content = r.content.decode()
        return r_content
