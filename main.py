import sys
from func.enterprise_wechat import *

input_dict = json.loads(sys.argv[1])


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
    print(last_wc_token)

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


# 推送到叮叮
# 模块未完成
def push_to_dingding(data_content):
    pass


def run():
    for k, v in input_dict.items():
        if k == "wechat":
            for i in v:
                push_to_wechat(i)
        else:
            for i in v:
                push_to_dingding(i)


if __name__ == "__main__":
    run()
