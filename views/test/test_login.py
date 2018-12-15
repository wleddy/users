
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

# These are used in other tests that need to login
def login(client, username=None, password=None):
    if not username and not password:
        username = 'admin'
        password = 'password'

    # have to call with get first to set the session cookie or no login
    result = client.get('/login/', follow_redirects=True)
    return client.post('/login/', data=dict(
        userNameOrEmail=username,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout/', follow_redirects=True)
        
        
def delete_test_db():
        os.remove(filespec)

def test_login(client):
    with client as c:
        from flask import session, g, request
        result = c.get('/login/')   
        assert result.status_code == 200
        assert b'User Name or Email Address' in result.data 

        result = c.post('/login/', data={'userNameOrEmail': 'admin', 'password': 'password'},follow_redirects=True)
        assert result.status == '200 OK'
        assert b'Invalid User Name or Password' not in result.data
        assert session['user'] == 'admin'
        ## don't test the resulting page... it is part of the overlying app
        #assert b'Hello' in result.data
        
        result = c.get('/logout/',follow_redirects=True)   
        assert result.status_code == 200
        assert b'Logged Out' in result.data 
        assert 'user' not in session
        
        result = c.post('/quiet_test/', data={'password': 'dog', 'password': 'password'},follow_redirects=True)
        assert result.status == '200 OK'
        assert b'Login Required' in result.data
        assert 'user' not in session
        
        result = c.post('/quiet_test/', data={'username': 'admin', 'password': 'password'},follow_redirects=True)
        #print(result.data)
        #print(g.user)
        #print(request.form['password'])
        assert result.status == '200 OK'
        assert b'Login Required' not in result.data
        assert session['user'] == 'admin'
        assert b'Ok' in result.data
        
        #Now should be able to work without password
        result = c.get('/logout/',follow_redirects=True)   
        assert result.status_code == 200
        assert 'user' not in session

    
        
############################ The final 'test' ########################
######################################################################
def test_finished():
    try:    
        db.close()
        delete_test_db()
        assert True
    except:
        assert True
