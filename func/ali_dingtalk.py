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


# 创建群聊
def create_dingding_chat():
    print("# 请输入钉钉应用的appKey：")
    app_key = input()

    print("\n# 请输入钉钉应用的appSecret：")
    app_secret = input()

    print("\n# 请输入告警群聊的名称，长度限制为1至20个字符：")
    chat_room_name = input()

    print("\n# 请输入告警群所有人的userid：")
    chat_room_owner = input()

    print("\n# 请确认新成员是否可查看聊天历史消息，告警群建立后可手动修改：")
    print("# 0：不允许")
    print("# 1：允许")
    show_history_type = input()

    print("\n# 请确认告警群是否可被搜索到，告警群建立后可手动修改：")
    print("# 0：不可被搜索")
    print("# 1：可被搜索")
    searchable = input()

    print("\n# 请确认入群是否需要管理员验证，告警群建立后可手动修改：")
    print("# 0：无需验证")
    print("# 1：需验证")
    validation_type = input()

    print("\n# 请确认告警群的 @all 功能权限，告警群建立后可手动修改：")
    print("# 0：所有人均有权限")
    print("# 1：仅该告警群主有权限")
    mention_all_authority = input()

    print("\n# 请确认是否开启全员禁言功能，告警群建立后可手动修改：")
    print("# 0：不开启")
    print("# 1：开启")
    chat_banned_type = input()

    ali_main = AliDingTalk(app_key, app_secret)

    # token
    last_ali_token = ali_main.chk_token()

    # 若旧token无效则获取新token
    if last_ali_token is None:
        new_ali_token = ali_main.get_token()

        if new_ali_token[0]:
            wc_token = new_ali_token[1]
        else:
            return new_ali_token[1]
    # 若旧token有效则使用旧token
    else:
        wc_token = json.dumps(last_ali_token)

    url = 'https://oapi.dingtalk.com/chat/create?access_token=' + wc_token
    post_content = {
        "name": chat_room_name,
        "owner": chat_room_owner,
        "useridlist": [chat_room_owner],
        "showHistoryType": show_history_type,
        "searchable": searchable,
        "validationType": validation_type,
        "mentionAllAuthority": mention_all_authority,
        "chatBannedType": chat_banned_type,
        "managementType": 1
    }
    msg_content = json.dumps(post_content, ensure_ascii=False)
    r = requests.post(url, msg_content.encode('utf-8'), timeout=5)
    r_content = r.content.decode()
    content_dict = json.loads(r_content)

    if content_dict["errcode"] == 0:
        output_content = "# 名为 " + chat_room_name + " 的告警群已建立，请记录chatid用于后续操作：" + content_dict["chatid"]
        return output_content
    else:
        output_content = "# 您输入的信息有误，阿里钉钉返回了错误信息，请留意告警信息内容：" + r_content
        return output_content


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
