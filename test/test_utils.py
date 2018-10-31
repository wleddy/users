import sys
import os

#print(sys.path)
sys.path.append('') ##get import to look in the working dir.

import users.utils as utils
from flask import g
import app

filespec = 'instance/test_user_utils.db'

db = None

with app.app.app_context():
    db = app.get_db(filespec)
    app.init_db(db)


def delete_test_db():
        os.remove(filespec)


def test_get_access_token():    
    with app.app.app_context():
        g.db = db
        
        t_len = 24
        token = utils.get_access_token()
        assert token is not None
        assert len(token) == t_len
    
        t_len = 18
        token = utils.get_access_token(t_len)
        assert token is not None
        assert len(token) == t_len
    
    
############################ The final 'test' ########################
######################################################################
def test_finished():
    try:    
        db.close()
        delete_test_db()
        assert True
    except:
        assert True
