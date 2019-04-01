import json
import os
from func.ali_dingtalk import *


def get_wechat_info():
    output_list = []

    while True:
        tmp_dict = dict()

        print("# 请输入企业微信的corpid：")
        wc_corpid = input()

        print("\n# 请输入企业微信的corpsecret：")
        wc_corpsecret = input()

        print("\n# 请输入企业微信的部门id：")
        wc_group_id = input()

        print("\n# 请输入企业微信的应用id：")
        wc_app_id = input()

        print("\n# 是否需要继续添加企业微信")
        print("\n# 1：继续添加")
        print("\n# 2：结束添加")
        keep_adding = input()

        tmp_dict['wc_corpid'] = wc_corpid
        tmp_dict['wc_corpsecret'] = wc_corpsecret
        tmp_dict['wc_group_id'] = wc_group_id
        tmp_dict['wc_app_id'] = wc_app_id

        output_list.append(tmp_dict)

        if keep_adding == 1:
            continue
        else:
            break

    return output_list


def get_dingding_info():
    output_list = []

    while True:
        tmp_dict = dict()

        print("# 请输入钉钉应用的appKey：")
        app_key = input()

        print("\n# 请输入钉钉应用的appSecret：")
        app_secret = input()

        print("\n# 请输入钉钉告警群的群id：")
        print("\n# 若无请留空并回车，接下来将引导您创建一个告警群")
        chat_room_id = input()

        if chat_room_id is '':

            print("\n# 请输入告警群聊的名称，长度限制为1至20个字符：")
            chat_room_name = input()

            print("\n# 请输入告警群所有人(群主)的userid：")
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
            ali_token = ali_main.get_token()

            if ali_token[0]:
                url = 'https://oapi.dingtalk.com/chat/create?access_token=' + ali_token[1]
            else:
                output_content = "# 您输入的信息有误，阿里钉钉返回了错误信息，请留意告警信息内容：" + ali_token[1]
                return output_content

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
                chat_room_id = content_dict["chatid"]
            else:
                output_content = "# 您输入的信息有误，阿里钉钉返回了错误信息，请留意告警信息内容：" + r_content
                return output_content

        print("\n# 是否需要继续添加企业微信")
        print("\n# 1. 继续添加")
        print("\n# 2. 结束添加")
        keep_adding = input()

        tmp_dict['app_key'] = app_key
        tmp_dict['app_secret'] = app_secret
        tmp_dict['chat_room_id'] = chat_room_id

        output_list.append(tmp_dict)

        if keep_adding == 1:
            continue
        else:
            break

    return output_list


def run():
    config_dict = dict()

    print("# 请问是否需要添加企业微信告警？")
    print("# 1：是")
    print("# 2：不是")
    add_wechat = input()

    print("# 请问是否需要添加钉钉告警？")
    print("# 1：是")
    print("# 2：不是")
    add_dingding = input()

    if add_wechat == "1":
        wechat_config_content = get_wechat_info()
        config_dict['wechat'] = wechat_config_content
    elif add_dingding == "1":
        dingding_config_content = get_dingding_info()
        config_dict['dingding'] = dingding_config_content
    else:
        pass

    config_file_path = os.getcwd() + '/alarm_sender.conf'
    o = open(config_file_path, 'w')
    o.write(str(config_dict))
    o.close()


if __name__ == "__main__":
    run()
