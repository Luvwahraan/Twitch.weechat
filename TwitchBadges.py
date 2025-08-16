VERSION='0.07'
import weechat
from weechat import prnt
from weechat import WEECHAT_RC_OK_EAT, WEECHAT_RC_OK
from typing import Type

weechat.register( \
        'TwitchBadges', \
        'Luvwahraan', \
        VERSION, \
        'GPLv3', \
        'Handle twitch badge tag', \
        "", "")

class B:
    # Empty class in order to permit Badge to use itself as Type
    pass
class Badge(B):
    def __init__(self, name, character=''):
        self.name = name
        self.character = character
        self.show = False
    
    def get(self):
        return self.character
    
    def showed(self):
        return self.show
    
    def showing(self):
        self.show = True
    def hiding(self):
        self.show = False
    
    def __repr__(self) -> str:
        return self.name
    
    def __eq__(self, badge:Type[B]) -> bool:
        if self.name == badge.name:
            return True
        return False
    def __eq__(self, badge:str) -> bool:
        if self.name == badge:
            return True
        return False


class Badges:
    """
    multi   limit badge displayed character
            defaut is only one
    """
    def __init__(self, multi=3):
        self.list = []
        self.multi = multi
        #self.list.append( Badge( 'broadcaster', '🎬' ) )
        self.list.append( Badge( 'broadcaster', '¡' ) )
        self.list.append( Badge( 'subscriber',  '+' ) )
        self.list.append( Badge( 'no-audio',    '🕨' ) )
        #self.list.append( Badge( 'no-video',    '🎧' ) )
        self.list.append( Badge( 'no-video',    '𝄞' ) )
        self.list.append( Badge( 'moderator',   '@' ) )
        self.list.append( Badge( 'vip',         'π' ) )
        self.list.append( Badge( 'sub-gifter',  'α' ) )
        self.list.append( Badge( 'founder',     'ƒ' ) )
        self.list.append( Badge( 'hype-train',  'Σ' ) )
        self.list.append( Badge( 'bits-leader', 'Ψ' ) )
        self.list.append( Badge( 'glhf-pledge', 'ω' ) )
        self.list.append( Badge( 'bits',        '¢' ) )
        self.list.append( Badge( 'turbo',       '-' ) )
        self.list.append( Badge( 'partner',     '$' ) )
        self.list.append( Badge( 'bits',        '⏶' ) )
        self.list.append( Badge( 'premium',     '≠' ) )
        self.list.append( Badge( 'random',      ' ' ) ) # espace insécable
        
    """
    Return badges string
    """
    def getBadges(self):
        badges_string = ''
        counter = self.multi
        for badge in self.list:
            if badge.showed():
                badges_string = f"{badges_string}{badge.get()}"
                counter = counter - 1
            if counter <= 0:
                break
    
        return badges_string
    
    """
    Search badge in list, and return it or False
    """
    def search(self, badge_name):
        #prnt('', f"Searching {badge_name}")
        for badge in self.list:
            if badge == badge_name:
                #prnt('', f"{badge_name} found: {badge.get()}" )
                return badge
        return False
    
    """
    Return True if badge created, False if exists already,
        and both case indicate to show it.
    """
    def add(self, badge_name, character=''):
        ret = False
        badge = self.search(badge_name)
        if badge == False:
            badge = Badge(badge_name, character)
            self.list.append( badge )
            ret = True
        #else:
        #    prnt('', f"Already known badge {badge_name}.")
        badge.showing()
            
        return ret
        
    def getCharacter(self, badge_name):
        badge = self.search(badge_name)
        if badge_name in self.list.items():
            self.list[badge_name]['show'] = True


class TwitchUser:
    def __init__(self, nick):
        self.badges = Badges()
        self.nick = nick
            
    """
    Add new or change badge.
    Return True if badge existed before.
    """
    def addBadge(self, badge_name):
        return self.badges.add(badge_name)
    
    def getBadges(self):
        return self.badges.getBadges()

def hookmodif_twitch_callback(data, modifier, modifier_data, string):
    msg = weechat.info_get_hashtable( 'irc_message_parse', {'message': string} )
    
    # Won't touch other than twitch messages.
    l = msg['host'].split(msg['nick'])
    if l[ len(l)-1 ] != '.tmi.twitch.tv':
        return string
        pass
    
    
    #for item in msg:
    #    prnt('', f"{item} : {msg[item]}")
    
    tUser = TwitchUser(msg['nick'])
    #modificator = ' '
    if 'tag_badges' in msg:
        for badge in msg['tag_badges'].split(','):
            #prnt('', f"{msg['nick']} »» {badge} ")
            if len(badge) > 0:
                badge_name, badge_time = badge.split('/')
                tUser.addBadge(badge_name)

    # Use empty modificator, if no badge.
    modificator = tUser.getBadges()
    if not modificator:
        #prnt('', "No badge.")
        modificator = ''
    else:
        modificator = f"{modificator} "
        #prnt('', f"Badges found: {modificator}")
        pass

    #prnt('', string)
    if 'tag_display-name' in msg and 'nick' in msg:
        nnick = f"{modificator}{msg['tag_display-name']}"
        nick = msg['nick']
        if nick != nnick:
            #prnt('', f"{nick} --> {nnick}")
            newstring = string.replace(f":{nick}", f":{nnick}")
            #newstring = string.replace(nick, f"{nnick}")
            if string != newstring:
                #prnt('', newstring)
                pass
            return newstring
    
        
    return string
    
    
    host = msg['host']
    channel = msg['channel']
    
    
weechat.hook_modifier('irc_in2_PRIVMSG', 'hookmodif_twitch_callback', '')
