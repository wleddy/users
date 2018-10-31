"""users.utils
    Some utility functions
"""

from flask import g
import random
    
def get_access_token(token_length=24):
    """Return an access token that does not exist in the user table"""
    from users.models import User
    
    temp_rec = 'temp'
    while temp_rec != None:
        access_token = ""
        for x in range(token_length):
            access_token += random.choice('abcdefghijklmnopqrstuvwxyz12344567890')
        #test that access_token is unique. break when rec == None
        temp_rec = User(g.db).select_one(where='access_token = "{}"'.format(access_token))
            
    return access_token
    
