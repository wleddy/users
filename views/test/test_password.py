import sys
#print(sys.path)
sys.path.append('') ##get import to look in the working dir.

        
def test_password():
    import users.views.password as login
    # basic tests
    passwords = ("password", 
                 "PassWord",
                 "nota passwoerd",
                 "password ",
                )
    results = ()
    for x in range(len(passwords)):
        results += (login.getPasswordHash(passwords[x]),)
        
    for x in range(len(passwords)):
        print('Basic test {}; pw: {}, hash: {}'.format(x,passwords[x],results[x]))
        assert results[x] != ''
        print(len(results[x]))
        assert len(results[x]) == 84
        if x > 0:
            assert results[x] != results[x-1]
    
    ### test the helper method to test a password
    for x in range(len(passwords)):
        print('Match test {}; pw: {}, hash: {}'.format(x,passwords[x],results[x]))
        assert login.matchPasswordToHash(passwords[x],results[x])
        
    ### test the None inputs and returns
    assert login.getPasswordHash('') == None
    assert login.matchPasswordToHash('',4) == False
    assert login.matchPasswordToHash('password','') == False
    assert login.matchPasswordToHash('password',234234) == False
    assert login.matchPasswordToHash('password',None) == False
    assert login.matchPasswordToHash(None,None) == False
    
