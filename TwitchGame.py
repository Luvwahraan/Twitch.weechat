# -*- coding: utf-8 -*-
import weechat
import requests
import time

SCRIPT_NAME    = 'TwitchGame'
SCRIPT_AUTHOR  = "Luvwahraan"
SCRIPT_VERSION = "0.02"
SCRIPT_LICENSE = "Whatever"
SCRIPT_DESC    = "A Touiche game."


token_cache = {
    "access_token": None,
    "expires_at": 0
}



def hookmodif_twitch_callback(data, modifier, modifier_data, privmsg):
    msg = weechat.info_get_hashtable( 'irc_message_parse', {'message': privmsg} )

    weechat.prnt( '', f"[{SCRIPT_NAME}] -- {msg}" )
    return privmsg


def set_credentials_command_cb(data, buffer, args):
    args_list = args.split(' ')
    if len(args_list) > 2:
        weechat.prnt('', f"[{SCRIPT_NAME}] Bad args.")
        weechat.prnt('', f"[{SCRIPT_NAME}] /{SCRIPT_NAME} client_id client_secret")
        return weechat.WEECHAT_RC_OK

    client_id = args_list[0]
    client_secret = args_list[1]
    
    weechat.config_set_plugin( 'client_id', client_id )
    weechat.config_set_plugin( 'client_secret', client_secret )
    
    return weechat.WEECHAT_RC_OK    


def get_config(option):
    return weechat.config_get_plugin(option)

def get_access_token(client_id, client_secret):
    #global token_cache

    now = time.time()
    if token_cache["access_token"] and now < token_cache["expires_at"]:
        return token_cache["access_token"]

    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    r = requests.post(url, params=params)
    if r.status_code == 200:
        data = r.json()
        token_cache["access_token"] = data.get("access_token")
        # expires_in = durée de vie en secondes
        expires_in = data.get("expires_in", 3600)
        token_cache["expires_at"] = now + expires_in - 30  # marge de 30s
        return token_cache["access_token"]

    return None

def get_avatar(username, client_id, token):
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {token}"
    }
    url = f"https://api.twitch.tv/helix/users?login={username}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json().get("data", [])
        if data:
            return data[0].get("profile_image_url")
    return None

def cmd_twitchavatar_cb(data, buffer, args):
    if not args:
        weechat.prnt(buffer, "Usage: /twitchavatar username")
        return weechat.WEECHAT_RC_OK

    username = args.strip()
    client_id = weechat.config_get_plugin("client_id")
    client_secret = weechat.config_get_plugin("client_secret")

    if not client_id or not client_secret:
        weechat.prnt(buffer, f"Configure credentials before use (/twitch_credentials client_id client_secret).")
        return weechat.WEECHAT_RC_OK

    token = get_access_token(client_id, client_secret)
    if not token:
        weechat.prnt(buffer, "Can't get OAuth token.")
        return weechat.WEECHAT_RC_OK

    avatar_url = get_avatar(username, client_id, token)
    if avatar_url:
        weechat.prnt(buffer, f"{username} avatar: {avatar_url}")
    else:
        weechat.prnt(buffer, f"Unable to get avatar: {username}.")

    return weechat.WEECHAT_RC_OK

# --- Script init ---
if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
    weechat.hook_command( "twitchavatar", "Get twitch user avatar url.",
            "<username>", "Exemple : /twitchavatar Luvwahraan", "",
            "cmd_twitchavatar_cb", "" )
    weechat.hook_command( 'twitch_credentials', 'Add update token for a twitch server.', 
            '', '', '',
            'set_credentials_command_cb', '' )

    #weechat.hook_modifier('irc_in2_PRIVMSG', 'hookmodif_twitch_callback', '')


