from users.utils import getDatetimeFromString
from datetime import datetime

# some custom filters for templates

def short_date_string(value, format='%-m/%-d/%y'):
    if value is None or value == "":
        # test if value is None or the empty string
        return value
    if type(value) is datetime:
        return value.strftime(format)
    if type(value) is str:
        return getDatetimeFromString(value).strftime(format)
    
    return value
    
    
def two_digit_string(the_string):
    #import pdb;pdb.set_trace()
    try:
        the_string = float(the_string)
        the_string = (str(the_string) + "00")
        pos = the_string.find(".")
        if pos > 0:
            the_string = the_string[:pos+3]
    except ValueError as e:
        pass
        
    return the_string
    

def register_jinja_filters(app):
    # register the filters
    app.jinja_env.filters['short_date_string'] = short_date_string
    app.jinja_env.filters['money'] = two_digit_string
