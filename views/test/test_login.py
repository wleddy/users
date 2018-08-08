
import sys
#print(sys.path)
sys.path.append('') ##get import to look in the working dir.

import os
import pytest
import tempfile

import app

@pytest.fixture
def client():
    db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
    app.app.config['TESTING'] = True
    client = app.app.test_client()

    with app.app.app_context():
        #print(app.app.config['DATABASE'])
        app.init_db(app.get_db(app.app.config['DATABASE'])) 
        #print(app.g.db)
        
    yield client

    os.close(db_fd)
    os.unlink(app.app.config['DATABASE'])
    
    
filespec = 'instance/test_login.db'

db = None

with app.app.app_context():
    db = app.get_db(filespec)
    app.init_db(db)

        
def delete_test_db():
        os.remove(filespec)

def test_login(client):
    with client as c:
        from flask import session, g
        result = c.get('/login/')   
        assert result.status_code == 200
        assert b'User Name or Email Address' in result.data 

        result = c.post('/login/', data={'userNameOrEmail': 'admin', 'password': 'password'},follow_redirects=True)
        assert result.status == '200 OK'
        assert b'Invalid User Name or Password' not in result.data
        assert session['user'] == 'admin'
        ## don't test the resulting page... it is part of the overlying app
        #assert b'Hello' in result.data
    
    
############################ The final 'test' ########################
######################################################################
def test_finished():
    try:    
        db.close()
        delete_test_db()
        assert True
    except:
        assert True
