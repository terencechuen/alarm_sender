import sys
from func.tencent_wechat import *
from func.ali_dingtalk import *

input_argv = sys.argv[1]


# 写入日志
# 模块未完成
def write_log(log_content):
    log_path = os.getcwd() + '/zabbix_alarm_sender.log'
    o = open(log_path, 'a')
    o.write(log_content + '\n')
    o.close()


# 推送到企业微信
def push_to_wechat(data_content):
    corp_id = data_content['corp_id']
    corp_secret = data_content['corp_secret']
    division_id = data_content['division_id']
    app_id = data_content['app_id']
    msg = data_content['msg']

    wechat_main = EnterpriseWeChat(corp_id, corp_secret, division_id, app_id)
    last_wc_token = wechat_main.chk_token()

    # 若旧token无效则获取新token
    if last_wc_token is None:
        new_wc_token = wechat_main.get_token()

        if new_wc_token[0]:
            wc_token = new_wc_token[1]
        else:
            return None
    # 若旧token有效则使用旧token
    else:
        wc_token = last_wc_token

    send_msg = wechat_main.send_msg(wc_token, msg)
    write_log(send_msg)
    return send_msg


# 推送到叮叮
# 模块未完成
def push_to_dingding(data_content):
    appkey = data_content['appkey']
    appsecret = data_content['appsecret']
    chatid = data_content['chatid']
    msg = data_content['msg']

    ali_main = AliDingTalk(appkey, appsecret)
    last_ali_token = ali_main.chk_token()

    # 若旧token无效则获取新token
    if last_ali_token is None:
        new_ali_token = ali_main.get_token()

        if new_ali_token[0]:
            wc_token = new_ali_token[1]
        else:
            return None
    # 若旧token有效则使用旧token
    else:
        wc_token = last_ali_token

    send_msg = ali_main.send_msg(wc_token, chatid, msg)
    write_log(send_msg)
    return send_msg


def run():
    if input_argv == "create_dingding_chat_room":
        print(create_dingding_chat())
    else:
        input_dict = json.loads(sys.argv[1])

        for k, v in input_dict.items():
            if k == "wechat":
                for i in v:
                    push_content = push_to_wechat(i)
                    print(push_content)
            else:
                for i in v:
                    push_content = push_to_dingding(i)
                    print(push_content)


if __name__ == "__main__":
    run()
