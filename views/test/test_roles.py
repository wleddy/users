
import sys
#print(sys.path)
sys.path.append('') ##get import to look in the working dir.

import os
import pytest
import tempfile

import app
from users.views.login import getPasswordHash

@pytest.fixture
def client():
    db_fd, app.app.config['DATABASE_PATH'] = tempfile.mkstemp()
    app.app.config['TESTING'] = True
    client = app.app.test_client()

    with app.app.app_context():
        print(app.app.config['DATABASE_PATH'])
        app.init_db(app.get_db(app.app.config['DATABASE_PATH']))
        # Add some more users
        f = open('users/views/test/test_data_create.sql','r')
        sql = f.read()
        f.close()
        cur = app.g.db.cursor()
        cur.executescript(sql)
        # doris and John need passwords
        rec = app.User(app.g.db).get('doris')
        rec.password = getPasswordHash('password')
        app.User(app.g.db).save(rec)
        rec = app.User(app.g.db).get('John')
        rec.password = getPasswordHash('password')
        app.User(app.g.db).save(rec)
        app.g.db.commit()
        
        rec = app.User(app.g.db).get('doris')
        print(rec)
        rec = app.User(app.g.db).get('John')
        print(rec)
        
    yield client

    os.close(db_fd)
    os.unlink(app.app.config['DATABASE_PATH'])
    
    
filespec = 'instance/test_roles.db'
db = None

with app.app.app_context():
    db = app.get_db(filespec)
    app.init_db(db)

        
def delete_test_db():
        os.remove(filespec)

    
def test_roles():
    from users.models import Role
    #db = get_test_db()
    
    assert Role(db).get(0) == None 
    
    recs = Role(db).select()
    assert recs != None
    assert len(recs)==3
    assert recs[0].name != None
    
    rec = Role(db).new()
    rec.name = "Testing"
    rec.description = "A test role"
    
    recID = Role(db).save(rec)
    rec = Role(db).get(recID)
    assert rec.id == recID
    assert rec.name == 'Testing'
    assert rec.rank == 0
    
    #Modify the record
    rec.name = "New Test"
    rec.rank = 300
    Role(db).save(rec)
    rec = Role(db).get(rec.id)
    assert rec.name == "New Test"
    assert rec.rank == 300
    
    db.rollback()
    
def nogood_test_list_page(client):
    """Right now this fails missurably, but when it was 'working' it was operating on the live database instead
    of the temporary one like the docs implied it would."""
    with app.app.app_context():
        with client as c:
            from flask import session, g
            from users.models import User,Role
            import app
            print(app.app.config['DATABASE_PATH'])
            app.get_db(app.app.config['DATABASE_PATH'])
            # access without login
            result = c.get('/user/delete/3/',follow_redirects=True)  
            assert result.status_code == 200
            assert b'Permission Denied' in result.data
        
            rec = User(app.g.db).get('John')
            print(rec)
        
            # Login as user role
            result = c.post('/login/', data={'userNameOrEmail': 'John', 'password': 'password'},follow_redirects=True)
            assert result.status == '200 OK'
            assert b'Invalid User Name or Password' not in result.data
            assert session['user'] == 'John'
        
            #attempt to delete a record
            result = c.get('/role/delete/3/',follow_redirects=True)  
            assert result.status_code == 200
            assert b'Permission Denied' in result.data
    
    
############################ The final 'test' ########################
######################################################################
def test_finished():
    try:
        db.close()
        delete_test_db()
        assert True
    except:
        assert True
