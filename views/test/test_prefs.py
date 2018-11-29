
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

    # get is now case in-sensitive
    rec = Pref(db).get('testing')
    assert rec.name == 'Testing'
    assert rec.value == "A test value"

    #Modify the record
    rec.name = "New Test"
    Pref(db).save(rec)
    rec = Pref(db).get(rec.id)
    assert rec.name == "New Test"
    
    db.rollback()
    
    # test the default setting
    pref_name = "A new pref"
    default_value = "A Default value"
    rec = Pref(db).get(pref_name)
    assert rec == None
    
    rec = Pref(db).get(pref_name,default=default_value)
    assert rec != None
    assert rec.name == pref_name
    assert rec.value == default_value
    
    # this should have no effect
    db.rollback()
    
    rec = Pref(db).get(pref_name)
    assert rec != None
    assert rec.name == pref_name
    assert rec.value == default_value
    
    
    #new pref was committed, so delete it
    assert Pref(db).delete(rec.id) == True
    db.commit()
    
    #Test that it's really gone
    rec = Pref(db).get(pref_name)
    assert rec == None
    
############################ The final 'test' ########################
######################################################################
def test_finished():
    try:
        db.close()
        delete_test_db()
        assert True
    except:
        assert True
