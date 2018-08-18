import sys
#print(sys.path)
sys.path.append('') ##get import to look in the working dir.

        
def test_password():
    from users.views import password
    # basic tests
    passwords = ("password", 
                 "PassWord",
                 "nota passwoerd",
                 "password ",
                )
    results = ()
    for x in range(len(passwords)):
        results += (password.getPasswordHash(passwords[x]),)
        
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
        assert password.matchPasswordToHash(passwords[x],results[x])
        
    ### test the None inputs and returns
    assert password.getPasswordHash('') == None
    assert password.matchPasswordToHash('',4) == False
    assert password.matchPasswordToHash('password','') == False
    assert password.matchPasswordToHash('password',234234) == False
    assert password.matchPasswordToHash('password',None) == False
    assert password.matchPasswordToHash(None,None) == False
    
