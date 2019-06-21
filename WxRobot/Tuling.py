from WxRobot import config
import requests

from wxpy import *

tuling = Tuling(api_key=config.tuling_api_key)

#自动回复
def autoReply(msg):
    return tuling.do_reply(msg)