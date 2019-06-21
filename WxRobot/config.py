tuling_api_key ='88f17f853d974387af64955bed9466f4'


# 自动回复
is_friend_auto_reply = True  # 好友自动回复
is_group_reply = True  # 此项表示群中是否回复
is_group_at_reply = True  # 上一项开启后此项才生效
is_forward_revoke_msg = True  # 开启防撤回模式
is_forward_group_at_msg = False  # 转发群@我的消息
is_record_send_msg=False #是否记录我发的消息

# 幕后黑手
bot_master_name = '小钱'  # 使用备注名，有远程控制功能，如果不设置(空)则将文件助手设置为管理员，但不具备远程控制功能

# 监听某些好友群聊，如老板
is_listen_friend = True
listen_friend_names = '俞立栋|张育豪|Slience雪鲤鱼|黄康|赞|远方的星星|小钱'  # 需要监听的人名称，使用备注名更安全，多个用|分隔
listen_friend_groups = '223'  # 在这些群里监听好友说的话


# 转发信息至群
is_forward_mode = True  # 打开转发模式，主人发送给机器人的消息都将转发至forward_groups群
forward_groups = '223'  # 需要将消息转发的群，匹配模式同上

# 群分享监控
is_listen_sharing = True
listen_sharing_groups = '223'  # 监控群分享，匹配模式同上