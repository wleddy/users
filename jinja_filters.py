from date_utils import getDatetimeFromString, date_to_string
from datetime import datetime

# some custom filters for templates
def iso_date_string(value):
    format = '%Y-%m-%d'
    return date_to_string(value,format)
        
        
def short_date_string(value):
    format='%m/%d/%y'
    return date_to_string(value,format)
    
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
    app.jinja_env.filters['iso_date_string'] = iso_date_string
