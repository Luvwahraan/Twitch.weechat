# -*- coding: utf-8 -*-
import weechat
import requests

SCRIPT_NAME    = "twitch_oauth"
SCRIPT_AUTHOR  = "Luvwahraan"
SCRIPT_VERSION = "1.0"
SCRIPT_LICENSE = "Whatever"
SCRIPT_DESC    = "OAuth Twitch auto update"

REFRESH_TOKEN = ''
IRC_SERVER = 'twitch'
EXPIRE_TIME = ''

cfg_refresh_token = "plugins.var.python.twitch_oauth.refresh_token"
cfg_irc_server =    "plugins.var.python.twitch_oauth.irc_server"
cfg_expire_time =   "plugins.var.python.twitch_oauth.expire_time"


def refresh_oauth_cb(data, remaining_calls):
    REFRESH_TOKEN = weechat.config_string( weechat.config_get(cfg_refresh_token) )
    url = f"https://twitchtokengenerator.com/api/refresh/{REFRESH_TOKEN}"

    try:
        response = requests.post(url)
        if response.status_code == 200:
            data = response.json()
            new_token = data['token']

            irc_server = weechat.config_string(  weechat.config_get(cfg_irc_server) )
            weechat.command("", f"/set irc.server.{irc_server}.password oauth:{new_token}")
            weechat.command("", f"/save irc")
            #weechat.command("", f"/reconnect {IRC_SERVER}")

            # Next token update
            expire_time = weechat.config_integer( weechat.config_get(cfg_expire_time) )
            next_timer = int((expire_time - 9000) * 1000)  # 9000s = 2h30
            weechat.hook_timer(next_timer, 0, 1, "refresh_oauth_cb", "")

            return weechat.WEECHAT_RC_OK
        else:
            raise Exception(f"Erreur HTTP lors du renouvellement: {response.status_code}")
    except Exception as e:
        weechat.prnt("", f"[{SCRIPT_NAME}] {e}")
        weechat.hook_timer(60000, 0, 1, "refresh_oauth_cb", "") # retries after 60s
        return weechat.WEECHAT_RC_OK


if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, 
                    SCRIPT_LICENSE, SCRIPT_DESC, "", ""):

    # check script config
    script_options = {
        cfg_refresh_token:  "please set refresh token",
        cfg_irc_server:     "twitch",
        cfg_expire_time:    "5184000",
    }
    for option, default_value in script_options.items():
        if not weechat.config_is_set_plugin(option):
            weechat.config_set_plugin(option, default_value)

    weechat.hook_timer(5000, 0, 1, "refresh_oauth_cb", "")

