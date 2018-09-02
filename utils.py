"""users.utils
    Some utility functions
"""

from flask import g
from datetime import datetime, timedelta
import linecache
import sys
import re
import random
import mistune # for Markdown rendering
import os


def cleanRecordID(id):
    """ return the integer version of id or else -1 """
    if id is None:
        return -1
    if type(id) is str: # or type(id) is unicode:
        if id.isdigit():
            # a negative number like "-1" will fail this test, which is what we want
            return int(id)
        else:
            return -1
            
    #already a number 
    return id
    
def looksLikeEmailAddress(email=""):
    """Return True if str email looks like a normal email address else False"""
    if type(email) is not str:
        return False
        
    return re.match(r"[^@]+@[^@]+\.[^@]+", email.strip())
    
def printException(mes="An Unknown Error Occured",level="error",err=None):
    from app import app
    exc_type, exc_obj, tb = sys.exc_info()
    debugMes = None
    if tb is not None:
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        try:
            debugMes = 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)
        except ValueError:
            debugMes = "Could not get error location info."
            
    if level=="error" or app.config["DEBUG"]:
        #always log errors
        if debugMes:
            app.logger.error(nowString() + " - " + debugMes)
        app.logger.error(nowString() + "   " + mes)
        if err:
            app.logger.error(nowString() + "    " + str(err))
        
    if app.config["DEBUG"]:
        if debugMes:
            mes = mes + " -- " +debugMes
        return mes
    else:
        return mes
    
def nowString():
    """Return the timestamp string in the normal format"""
    return datetime.now().isoformat()[:19]
    
def get_access_token(token_length=24):
    """Return an access token that does not exist in the user table"""
    from users.models import User
    
    temp_rec = 'temp'
    while temp_rec != None:
        access_token = ""
        for x in range(token_length-1):
            access_token += random.choice('abcdefghijklmnopqrstuvwxyz12344567890')
        #test that access_token is unique. break when rec == None
        temp_rec = User(g.db).select_one(where='access_token = "{}"'.format(access_token))
            
    return access_token
    
    
def render_markdown_for(source_script,module,file_name):
    """Try to find the file to render and then do so"""
    rendered_html = ''
    # use similar search approach as flask templeting, root first, then local
    # try to find the root templates directory
    markdown_path = os.path.dirname(os.path.abspath(__name__)) + '/templates/{}'.format(file_name)
    if not os.path.isfile(markdown_path):
        # look in the templates directory of the calling blueprint
        markdown_path = os.path.dirname(os.path.abspath(source_script)) + '/{}/{}'.format(module.template_folder,file_name)
    if os.path.isfile(markdown_path):
        f = open(markdown_path)
        rendered_html = f.read()
        f.close()
        rendered_html = render_markdown_text(rendered_html)

    return rendered_html
    
def render_markdown_text(text_to_render):
    return mistune.markdown(text_to_render)
       
##############################################################################################
## These are functions left over from bikeandwalk. Don't think I need them, but you never know
##############################################################################################
#

#def getDatetimeFromString(dateString):
#    if type(dateString) is str: # or type(dateString) is unicode:
#        pass
#    else:
#        return None
#        
#    dateString = dateString[:19]
#    timeDelimiter = " "
#    if "T" in dateString:
#        timeDelimiter = "T"
#
#    formatString = '%Y-%m-%d'+timeDelimiter+'%H:%M:%S'
#    try:
#        theDate = datetime.strptime(dateString, formatString) ## convert string to datetime
#    except Exception as e:
#        printException("Bad Date String","error",e)
#        theDate = None
#        
#    if theDate == None:
#        return None
#        
#    return theDate.replace(microsecond=0)
#
#
#def getLocalTimeAtEvent(tz,isDST=0):
#    """
#        Return the current local time at an event location
#    """
#    localTime = datetime.utcnow() + timedelta(hours=(getTimeZoneOffset(tz))) ## get local time at the event location
#    if(isDST == 1):
#        localTime = localTime + timedelta(hours=1)
#    
#    return localTime.replace(microsecond=0)
#    
#def getTimeZones():
#    # return a dictionary of time zone names and offsets
#    tz = {"EST":{"longName" : 'New York US', "offset": -5}, 
#          "CST":{"longName" : 'Chicago US', "offset": -6},
#          "MST":{"longName" : 'Denver US', "offset": -7},
#          "PST":{"longName" : 'Los Angeles US', "offset": -8},
#         }
#    return tz
#    
#def getTimeZoneOffset(zone=""):
#    tz = getTimeZones()
#    try:
#        return tz[zone.upper()]["offset"]
#    except KeyError:
#        return 0
#    
