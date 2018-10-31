import sys
#print(sys.path)
sys.path.append('') ##get import to look in the working dir.

import takeabeltof.utils as utils

def test_cleanRecordID():
    """Tesst the cleanRecordID utility fuction"""
    
    assert utils.cleanRecordID(1234) == 1234
    assert utils.cleanRecordID("1234") == 1234
    assert utils.cleanRecordID("this is a test4455") == -1
    assert utils.cleanRecordID("1234this is a test") == -1
    assert utils.cleanRecordID(-4) == -4
    assert utils.cleanRecordID('-4') == -1
    assert utils.cleanRecordID(None) == -1
    

def test_looksLikeEmailAddress():
    """Does this string look like an email address?"""
    assert utils.looksLikeEmailAddress("bill@example.com")
    assert utils.looksLikeEmailAddress("bill.leddy@example.com")
    assert utils.looksLikeEmailAddress() != True
    assert utils.looksLikeEmailAddress(2343345) != True
    assert utils.looksLikeEmailAddress("@Exmaple.com") != True
    assert utils.looksLikeEmailAddress("bill@example") != True
    