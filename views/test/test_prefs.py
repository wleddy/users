
import sys
#print(sys.path)
sys.path.append('') ##get import to look in the working dir.

import os
import pytest
import tempfile

import app
from users.views.password import getPasswordHash

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
    
    
filespec = 'instance/test_prefs.db'
db = None

with app.app.app_context():
    db = app.get_db(filespec)
    app.init_db(db)

        
def delete_test_db():
        os.remove(filespec)

    
def test_prefs():
    from users.models import Pref
    #db = get_test_db()
    
    assert Pref(db).get(0) == None 
    assert Pref(db).get("this") == None 
        
    rec = Pref(db).new()
    rec.name = "Testing"
    rec.value = "A test value"
    
    recID = Pref(db).save(rec)
    rec = Pref(db).get(recID)
    assert rec.id == recID
    assert rec.name == 'Testing'
    assert rec.value == "A test value"
    
    rec = Pref(db).get('Testing')
    assert rec.name == 'Testing'
    assert rec.value == "A test value"

    #Modify the record
    rec.name = "New Test"
    Pref(db).save(rec)
    rec = Pref(db).get(rec.id)
    assert rec.name == "New Test"
    
    db.rollback()
    
    
############################ The final 'test' ########################
######################################################################
def test_finished():
    try:
        db.close()
        delete_test_db()
        assert True
    except:
        assert True
