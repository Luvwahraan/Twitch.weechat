# -*- coding: utf-8 -*-
import weechat
import requests

SCRIPT_NAME    = "twitch_oauth"
SCRIPT_AUTHOR  = "Luvwahraan"
SCRIPT_VERSION = "1.0"
SCRIPT_LICENSE = "Whatever"
SCRIPT_DESC    = "OAuth Twitch auto update"


cfg_refresh_token = "plugins.var.python.twitch_oauth.refresh_token"
cfg_irc_server =    "plugins.var.python.twitch_oauth.irc_server"
#cfg_expire_time =   "plugins.var.python.twitch_oauth.expire_time"

#cfg_refresh_token = "irc.server.{irc_server}.twitch_oauth.refresh_token"
#cfg_irc_server =    "plugins.var.python.twitch_oauth.irc_server"
#cfg_expire_time =   "plugins.var.python.twitch_oauth.expire_time"

def update_request(irc_server):
    refresh_token = weechat.config_get_plugin( f"{irc_server}.refresh_token" )
    refresh_url = f"https://twitchtokengenerator.com/api/refresh/{refresh_token}"
    
    try:
        response = requests.post(refresh_url)
        if response.status_code == 200:
            data = response.json()
            new_token = data['token']

            #irc_server = weechat.config_string(  weechat.config_get(cfg_irc_server) )
            weechat.command("", f"/set irc.server.{irc_server}.password oauth:{new_token}")
            weechat.command("", f"/save irc")
            #weechat.command("", f"/reconnect {irc_server}")

            # Next token update
            expire_time = weechat.config_integer( weechat.config_get_plugin('expire_time') )
            next_timer = int((expire_time - 9000) * 1000)  # 9000s = 2h30
            weechat.hook_timer(next_timer, 0, 1, "refresh_oauth_cb", "")
        else:
            raise Exception(f"Erreur HTTP lors du renouvellement: {response.status_code}")
    except Exception as e:
        weechat.prnt('', f"[{SCRIPT_NAME}] {e}")
        weechat.hook_timer(60000, 0, 1, "refresh_oauth_cb", "") # retries after 60s
    
    return weechat.WEECHAT_RC_OK

def addserver_command_cb(data, buffer, args):
    
    args_list = args.split(' ')
    if len(args_list) > 2:
        weechat.prnt('', f"[{SCRIPT_NAME}] Bad args.")
        weechat.prnt('', f"[{SCRIPT_NAME}] /{SCRIPT_NAME} server refresh_token")
        return weechat.WEECHAT_RC_OK

    irc_server = args_list[0]
    refresh_token = args_list[1]

    cfg_token = f"{irc_server}.refresh_token"
    if not weechat.config_get_plugin(cfg_token):
        # unknown twitch server and oauth: adding

        irc_servers_str = weechat.config_get_plugin('irc_servers')
        
        # Comma separated list
        if irc_servers_str == '':
            weechat.config_set_plugin( 'irc_servers', irc_server )
        else:
            weechat.config_set_plugin( 'irc_servers', f"{irc_servers_str},{irc_server}" )

        weechat.config_set_plugin( cfg_token, refresh_token )
        weechat.prnt('', f"[{SCRIPT_NAME}] New refresh token for '{irc_server}'.")
        weechat.command("", "/save plugins")
    else:
        # no add
        weechat.prnt('', f"[{SCRIPT_NAME}] Refresh token already exists for '{irc_server}'.")
    
    return weechat.WEECHAT_RC_OK    

def refresh_oauth_cb(data, remaining_calls):
    servers_str = weechat.config_get_plugin('irc_servers')
    for irc_server in servers_str.split(','):
        # Don't try to with an update empty server string.
        if irc_server:
            update_request(irc_server)
    return weechat.WEECHAT_RC_OK



if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, 
                    SCRIPT_LICENSE, SCRIPT_DESC, "", ""):

    # check script config
    script_options = {
        'irc_servers':  '',
        'expire_time':  "5184000",
        #cfg_refresh_token:  "please set refresh token",
        #cfg_irc_server:     "twitch",
    }
    for option, default_value in script_options.items():
        if not weechat.config_get_plugin(option):
            weechat.config_set_plugin(option, default_value)

    weechat.hook_timer( 1500, 0, 1, "refresh_oauth_cb", "" )
    weechat.hook_command( SCRIPT_NAME, 'Add update token for a twitch server.', 
            '', '', '',
            'addserver_command_cb', '' )

