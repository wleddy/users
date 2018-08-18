###########################################
## admin.py
## Control what tables a user may access as an
## administrator.
###########################################

from flask import g, request, redirect, url_for, flash
from functools import wraps

class Admin():
    """Register tables to be administered then check a user's access permissions
    
    Instanciate as:
        admin = Admin(g.db)
        
    Register an admin table:
        Admin.register(TableObj,url,[,display_name=None[,minimum_rank_required=None[,roles=None]]])
        results in an item being added to self.permissions:
        self.permissions = [{table,display_name,url,minimum_rank_required(default = 99999999),roles(default = [])},]
        
        Registering a table again will replace the previous registration for that table.
    
    When assessing permissions test that the specified user (by id or username) has:
         a role with at least minimum_rank_required
         OR
         a role (by name) in the list roles
    """
    
    def __init__(self,db):
        self.db = db #A database connection. need it to instanciate tables
        self.permissions = []
        
    def register(self,table,url,**kwargs):
        """Add an item to the admin_list"""
        display_name=kwargs.get('display_name',None)
        minimum_rank_required=kwargs.get('minimum_rank_required',99999999) #No one can access without a qualifiying role
        roles=kwargs.get('roles',[])
        
        
        table_ref = table(self.db)
        if not display_name:
            display_name = table_ref.display_name
            
        permission = {'table':table,'display_name':display_name,'url':url,'minimum_rank_required':minimum_rank_required,'roles':roles}
        
        #test that table only has one permission
        for x in range(len(self.permissions)):
            if self.permissions[x]['table'] == table:
                self.permissions[x] = permission
                return
                
        self.permissions.append(permission)
           
    def has_access(self,user_name,table=None):
        """Test to see if the user represented by user name has access to ANY admin items
        If the display_name is specified, only check to see if user has access to that table"""
        from users.models import User
        
        if len(self.permissions) == 0:
            return False
            
        user = User(self.db)
        rec = user.get(user_name)
        if not rec or not user:
            return False
            
        user_roles = user.get_roles(rec.id)
        if not user_roles:
            return False
            
        temp_list = self.permissions
        if table:
            temp_list = [x for x in temp_list if x['table'] == table]
            
        for role in user_roles:
            for list_item in temp_list:
                if role.name in list_item['roles']:
                    return True
                if list_item['minimum_rank_required'] <= role.rank:
                    return True
                    
        return False
        

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash("Login Required")
            return redirect(url_for('login.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
    
def table_access_required(table):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from users.views.login import authenticate_user
            if g.user is None or not g.admin or not g.admin.has_access(g.user,table):
                flash("Permission Denied")
                return redirect(url_for('login.login', next=request.url))
            return f(*args,**kwargs)
        return decorated_function
    return decorator
    
    
def silent_login(f):
    """
        Expects a username and password in the POST data
        Try to login and return requested resource
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #import pdb;pdb.set_trace()
        from users.views.login import authenticate_user
        if g.user == None \
            and (not request.form \
            or 'username' not in request.form \
            or 'password' not in request.form \
            or authenticate_user(request.form["username"],request.form['password']) != 1):
            flash("Login Required")
            return redirect(url_for('login.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
    
