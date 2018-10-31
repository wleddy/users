from takeabeltof.database import SqliteTable
from takeabeltof.utils import cleanRecordID
from users.views.password import getPasswordHash
        
class Role(SqliteTable):
    """Handle some basic interactions with the role table"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'role'
        self.order_by_col = 'lower(name)'
        self.defaults = {'rank':0,}
        
    def create_table(self):
        """Define and create the role tablel"""
        
        sql = """
            'name' TEXT UNIQUE NOT NULL,
            'description' TEXT,
            'rank' INTEGER DEFAULT 0 """
        super().create_table(sql)
        
    def init_table(self):
        """Create the table and initialize data"""
        self.create_table()
        
        #Try to get a value from the table and create records if none
        rec = self.db.execute('select * from {}'.format(self.table_name)).fetchone()
        if not rec:
            roles = [
                (None,'super','Super User',1000),
                (None,'admin','Admin User',500),
                (None,'user','Normal user',1),
            ]
            self.db.executemany("insert into {} values (?,?,?,?)".format(self.table_name),roles)
            self.db.commit()


class UserRole(SqliteTable):
    """Handle some basic interactions with the user_role table"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'user_role'
    
    def create_table(self):
        """Define and create the user_role tablel"""
        
        sql = """
            'user_id' INTEGER NOT NULL,
            'role_id' INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES role(id) ON DELETE CASCADE """
        super().create_table(sql)
                
        
class User(SqliteTable):
    """Handle some basic interactions with the user table"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'user'
        self.order_by_col = 'last_name, first_name'
        self.defaults = {'active':1,}
        
    def _active_only_clause(self,include_inactive=False,**kwargs):
        """Return a clause for the select statement to include active only or empty string"""
        include_inactive = kwargs.get('include_inactive',include_inactive)
        if include_inactive:
            return ""
        
        return 'and active = 1'
        
    def add_role(self,user_id,role_id):
        self.db.execute('insert into user_role (user_id,role_id) values (?,?)',(cleanRecordID(user_id),cleanRecordID(role_id),))
        
    def delete(self,rec_id):
        """Delete a single user record as indicated
        'id' may be an integer or a string"""
        
        rec = self.get(rec_id,include_inactive=True)
        if rec:
            return super().delete(rec.id,include_inactive=True)
            
        return False
        
    def get(self,id,**kwargs):
        """Return a single namedlist for the user with this id
            A keyword argument for include_inactive controls filtering
            of active users only
        """
        #if the 'id' is a string, try to find the user by username or email
        if type(id) is str:
            return self.get_by_username_or_email(id,**kwargs)
            
        include_inactive = kwargs.get('include_inactive',False)
        where = 'id = {} {}'.format(cleanRecordID(id),self._active_only_clause(include_inactive))

        return self.select_one(where=where)

    def get_by_username_or_email(self,nameoremail,**kwargs):
        """Return a single namedlist obj or none based on the username or email"""

        include_inactive = kwargs.get('include_inactive',False)

        sql = "select * from {} where (username = ? or lower(email) = lower(?)) {} order by id".format(self.table_name,self._active_only_clause(include_inactive))
        
        return self._single_row(self.select_raw(sql,(nameoremail.strip(),nameoremail.strip())))
    
    def get_roles(self,userID,**kwargs):
        """Return a list of the role namedlist objects for the user's roles"""
        
        order_by = kwargs.get('order_by','rank desc, name')
        sql = """select * from role where id in
                (select role_id from user_role where user_id = ?) order by {}
                """.format(order_by)
                
        return  Role(self.db).rows_to_namedlist(self.db.execute(sql,(cleanRecordID(userID),)).fetchall())
                
    def select(self,**kwargs):
        """Limit selection to active user only unless 'include_inactive' is true in kwargs"""
        where = '{} {}'.format(kwargs.get('where','1'),self._active_only_clause(kwargs.get('include_inactive',False)))
            
        order_by = kwargs.get('order_by',self.order_by_col)
        
        return super().select(where=where,order_by=order_by)
        
    def update_last_access(self,user_id,no_commit=False):
        """Update the 'last_access field with the current datetime. Default is for record to be committed"""
        if type(user_id) is int:
            self.db.execute('update user set last_access = datetime() where id = ?',(user_id,))
            if not no_commit:
                self.db.commit()
                
    def clear_roles(self,user_id):
        """Delete all user_role records from this user"""
        self.db.execute('delete from user_role where user_id = ?',(cleanRecordID(user_id),))
        
    def create_table(self):
        """Define and create the user tablel"""
        
        sql = """
            'first_name' TEXT,
            'last_name' TEXT,
            'email' TEXT UNIQUE COLLATE NOCASE,
            'phone' TEXT,
            'address' TEXT,
            'address2' TEXT,
            'city' TEXT,
            'state' TEXT,
            'zip' TEXT,
            'username' TEXT UNIQUE,
            'password' TEXT,
            'active' INTEGER DEFAULT 1,
            'last_access' DATETIME,
            'access_token' TEXT,
            'access_token_expires' INT
            """
        super().create_table(sql)
        
    def init_table(self):
        """add some initial data"""

        self.create_table()
        
        #Try to get a value from the table and create a record if none
        rec = self.db.execute('select * from {}'.format(self.table_name)).fetchone()
        if not rec:
            sql = """insert into {}
                (first_name,last_name,username,password)
                values
                ('Admin','User','admin','{}')
            """.format(self.table_name,getPasswordHash('password'))
            self.db.execute(sql)
            #self.db.commit()
            
            # Give the user super powers
            rec = self.get(1)
            userID = rec.id
            rec = Role(self.db).select_one(where='name = "super"')
            roleID = rec.id
            self.db.execute('insert into user_role (user_id,role_id) values (?,?)',(userID,roleID))
            self.db.commit()


class Pref(SqliteTable):
    """
        A table to store some random data in
        Prefs can be global or attached to a single user
        Prefs can also be set to expire
    """
    
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'pref'
        self.order_by_col = 'name'
        self.defaults = {}
        
    def create_table(self):
        """Define and create the table"""

        sql = """
            name TEXT,
            value TEXT,
            expires DATETIME,
            user_name TEXT
            """
        super().create_table(sql)

    def get(self,name,user_name=None,**kwargs):
        """can get by pref name and user_name"""
        user_clause = ''
        if user_name:
            user_clause = ' and user_name = {}'.format(user_name)
        
        if type(name) is str:
            where = ' name = "{}" {}'.format(name,user_clause)
        else:
            where = ' id = {}'.format(cleanRecordID(name))
            
        return self.select_one(where=where)
        
        
def init_db(db):
    """Create a intial user record."""
    Role(db).init_table()
    UserRole(db).init_table()
    User(db).init_table()
    Pref(db).init_table()
    