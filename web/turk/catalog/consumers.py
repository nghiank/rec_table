from channels import Group
from channels.sessions import channel_session
from channels.auth import channel_session_user_from_http

@channel_session_user_from_http
def ws_connect(message):
    print("Group user-" + str(message.user))
    Group('user-' + str(message.user)).add(message.reply_channel)

@channel_session_user_from_http
def ws_disconnect(message):
    Group('user-'+str(message.user)).discard(message.reply_channel)
