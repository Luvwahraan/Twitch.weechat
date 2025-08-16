# -*- coding: utf-8 -*-
import weechat
import requests

SCRIPT_NAME    = "twitch_oauth"
SCRIPT_AUTHOR  = "Luvwahraan"
SCRIPT_VERSION = "1.0"
SCRIPT_LICENSE = "Whatever"
SCRIPT_DESC    = "Automatiquement OAuth Twitch update"

REFRESH_TOKEN = ''
IRC_SERVER = 'twitch'
EXPIRE_TIME = ''


def refresh_oauth_cb(data, remaining_calls):
    REFRESH_TOKEN = weechat.config_string( weechat.config_get(f"plugins.var.python.{SCRIPT_NAME}.refresh_token") )
    url = f"https://twitchtokengenerator.com/api/refresh/{REFRESH_TOKEN}"

    try:
        response = requests.post(url)
        if response.status_code == 200:
            data = response.json()
            new_token = data['token']

            # Met à jour WeeChat
            weechat.command("", f"/set irc.server.{IRC_SERVER}.password oauth:{new_token}")
            weechat.command("", f"/save")
            #weechat.command("", f"/reconnect {IRC_SERVER}")
            weechat.prnt("", f"[{SCRIPT_NAME}] Token Twitch mis à jour.")

            # Planifie le prochain renouvellement quelques heures avant expiration
            return int((EXPIRE_TIME - 9000) * 1000)  # 9000s = 2h30 avant expiration
        else:
            weechat.prnt("", f"[{SCRIPT_NAME}] Erreur HTTP lors du renouvellement: {response.status_code}")
            return 60000  # Réessaie dans 60s
    except Exception as e:
        weechat.prnt("", f"[{SCRIPT_NAME}] Exception lors du renouvellement: {e}")
        return 60000  # retries 60s after



def config_cb(data, option, value):
    REFRESH_TOKEN = weechat.config_string(  weechat.config_get(f"plugins.var.python.{SCRIPT_NAME}.refresh_token") )
    IRC_SERVER =    weechat.config_string(  weechat.config_get(f"plugins.var.python.{SCRIPT_NAME}.irc_server") )
    EXPIRE_TIME =   weechat.config_integer( weechat.config_get(f"plugins.var.python.{SCRIPT_NAME}.expire_time") )
    return weechat.WEECHAT_RC_OK


if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, 
                    SCRIPT_LICENSE, SCRIPT_DESC, "", ""):    
    REFRESH_TOKEN = weechat.config_string(  weechat.config_get(f"plugins.var.python.{SCRIPT_NAME}.refresh_token") )
    IRC_SERVER =    weechat.config_string(  weechat.config_get(f"plugins.var.python.{SCRIPT_NAME}.irc_server") )
    EXPIRE_TIME =   weechat.config_integer( weechat.config_get(f"plugins.var.python.{SCRIPT_NAME}.expire_time") )

    weechat.hook_timer(5000, 0, 1, "refresh_oauth_cb", "")
    weechat.hook_config("plugins.var.python." + SCRIPT_NAME + ".*", "config_cb", "")

