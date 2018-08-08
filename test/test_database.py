import sys
sys.path.append('') ##get import to look in the working dir.

filespec = 'instance/test_database.db'

db = None

def delete_test_db():
        os.remove(filespec)

def test_database():
    from users.database import Database
    db2 = Database(filespec)
    assert type(db2) is Database

############################ The final 'test' ########################
######################################################################
def test_finished():
    try:
        delete_test_db()
        assert True
    except:
        assert True
