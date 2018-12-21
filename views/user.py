from datetime import datetime
from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from takeabeltof.utils import printException, cleanRecordID, looksLikeEmailAddress, render_markdown_for
from time import time
from users.models import User, Role
from users.utils import get_access_token
from users.views.login import setUserStatus
from users.views.password import getPasswordHash
from users.admin import login_required, table_access_required


mod = Blueprint('user',__name__, template_folder='../templates', url_prefix='/user')


def setExits():
    g.listURL = url_for('.display')
    g.adminURL = url_for('.admin',id=0)
    g.editURL = url_for('.edit')
    g.registerURL = url_for('.register')
    g.deleteURL = url_for('.delete')
    g.homeURL = url_for('.home')
    g.title = 'User'

@mod.route('/')
@login_required
def home():
    setExits()
    return render_template('user/user_index.html')
    
@mod.route('/list/', methods=['GET'])
@table_access_required(User)
def display():
    setExits()
    g.title = "{} List".format(g.title)
    include_inactive = True
    
    recs = User(g.db).select(include_inactive=include_inactive)
    return render_template('user/user_list.html', recs=recs)
    
@mod.route('/edit/<int:id>/', methods=['POST','GET'])
@table_access_required(User)
def admin(id=None):
    """Administrator access for the User table records
    """
    setExits()
    if id == None:
        flash("No User identifier supplied")
        return redirect(g.listURL)
        
    #import pdb;pdb.set_trace()
        
    id = cleanRecordID(id)
    if(id < 0):
        flash("That is an invalid id")
        return redirect(g.listURL)
        
    #session['user_edit_token'] = id
    
    return edit(id)
    

## Edit the user
@mod.route('/edit', methods=['POST', 'GET'])
@mod.route('/edit/', methods=['POST', 'GET'])
@login_required
def edit(rec_handle=None):
    setExits()
    g.title = "Edit {} Record".format(g.title)
    #import pdb;pdb.set_trace()

    user = User(g.db)
    rec = None
    request_rec_id = cleanRecordID(request.form.get('id',request.args.get('id',-1)))
    is_admin = g.admin.has_access(g.user,User)
    no_delete = not is_admin
    session_roles = session["user_roles"] #roles of currnet user
    new_password = ''
    confirm_password = ''
    user_roles = ['user'] # default
    roles = Role(g.db).select()
    include_inactive = True
    
    if not is_admin:
        g.listURL = g.homeURL # Non admins can't see the list
        include_inactive = False
        
    if rec_handle != None:
        pass #rec_handle has to come from admin() at this point
    elif rec_handle == None and g.user != None and request_rec_id == -1:
        rec_handle = g.user
    else:
        rec_handle = request_rec_id
        if rec_handle < 0:
            flash("That is not a valid User ID")
            return redirect(g.listURL)
        
    if not request.form:
        """ if no form object, send the form page """
        if rec_handle != g.user and not is_admin:
            flash("You do not have access to that area")
            return redirect(g.homeURL)
        elif rec_handle == 0:
            rec = user.new()
        else:
            rec = user.get(rec_handle,include_inactive=include_inactive)
            if not rec:
                flash("Unable to locate user record")
                return redirect('/')
                
            user_roles = get_user_role_names(rec)
        
    else:
        #have the request form
        #import pdb;pdb.set_trace()
        is_new_user = False
        if rec_handle and request.form['id'] != 'None':
            rec = user.get(rec_handle,include_inactive=include_inactive)
            user_roles = get_user_role_names(rec)
        else:
            # its a new unsaved record
            is_new_user = True
            rec = user.new()
            user.update(rec,request.form)

        if validForm(rec):
        
            #Are we editing the current user's record?
            editingCurrentUser = ''
            if(g.user == rec.username):
                if 'new_username' in request.form:
                    editingCurrentUser = request.form['new_username'].strip()
                else:
                    editingCurrentUser = g.user
            else: 
                if(g.user == rec.email):
                    editingCurrentUser = request.form['email'].strip()
            
            #update the record
            user.update(rec,request.form)
            
            set_username_from_form(rec)        
            set_password_from_form(rec)
    
            try:
                user.save(rec)
                
                # update the user roles
                if 'roles_select' in request.form:
                    #delete all the users current roles
                    user.clear_roles(rec.id)
                    for role_name in request.form.getlist('roles_select'):
                        #find the role by name
                        role = Role(g.db).select_one(where='name = "{}"'.format(role_name))
                        if role:
                            user.add_role(rec.id,role.id)
                    
                # if the username or email address are the same as g.user
                # update g.user if it changes
                if(editingCurrentUser != ''):
                    setUserStatus(editingCurrentUser,rec.id)
                    
                g.db.commit()
                
            except Exception as e:
                g.db.rollback()
                flash(printException('Error attempting to save '+g.title+' record.',"error",e))
                return redirect(g.listURL)
                
            if is_new_user == True and rec.email:
                from takeabeltof.mailer import send_message
                
                # send an email to welcome the new user
                full_name = '{} {}'.format(rec.first_name,rec.last_name).strip()
                
                context = {'rec':rec,'full_name':full_name,}
                to_address_list=[(full_name,rec.email)]
                sent,msg = send_message(
                    to_address_list,
                    subject="Welcome to {{config.SITE_NAME}}",
                    context=context,
                    html_template='user/email/welcome.html',
                    text_template='user/email/welcome.txt',
                    )
                if not sent:
                    flash('The welcome message could not be sent. Error: {}'.format(msg))
                    
            return redirect(g.listURL)
        
        else:
            # form did not validate, give user the option to keep their old password if there was one
            #need to restore the username
            user.update(rec,request.form)
            if 'new_username' in request.form:
                rec.username = request.form['new_username'] #preserve user input
            # preserve the selected roles
            #import pdb;pdb.set_trace()
            if 'roles_select' in request.form:
                user_roles = request.form.getlist('roles_select')
            #and password
            new_password = request.form.get('new_password','')
            confirm_password = request.form.get('confirm_password','')

    # display form
    return render_template('user/user_edit.html', rec=rec, 
        no_delete=no_delete, 
        is_admin=is_admin, 
        user_roles=user_roles, 
        roles=roles,
        session_roles=session_roles,
        new_password=new_password,
        confirm_password=confirm_password,
        )
    
@mod.route('/register/', methods=['GET','POST'])
def register():
    """Allow people to sign up thier own accounts on the web site"""
    setExits()
    g.title = "Account Registration"
    g.editURL = url_for('.register')
    g.listURL = '/' # incase user cancels
    user = User(g.db)
    rec=user.new()
    
    from takeabeltof.mailer import send_message
    from app import app
    
    is_admin = False
    user_roles=None
    roles=None
    no_delete=True
    success=True
    help = render_markdown_for(__file__,mod,"user/new_account_help.md")        
    
    if 'confirm' in request.args:
        #Try to find the user record that requested registration
        rec=user.select_one(where='access_token = "{}"'.format(request.args.get('confirm','')).strip())
        if rec and rec.access_token_expires > time():
            if rec.active == 1:
                success="active"
            else:
                success="waiting"
                
            #inform the admin
            to=[(app.config['MAIL_DEFAULT_SENDER'],app.config['MAIL_DEFAULT_ADDR'])]
            confirmURL = "{}://{}{}?activate={}".format(app.config['HOST_PROTOCOL'],app.config['HOST_NAME'],url_for('.activate'), rec.access_token)
            deleteURL = "{}://{}{}?delete={}".format(app.config['HOST_PROTOCOL'],app.config['HOST_NAME'],url_for('.delete'), rec.access_token)
            context={'rec':rec,'confirmURL':confirmURL,'deleteURL':deleteURL}
            subject = 'Activate Account Request from - {}'.format(app.config['SITE_NAME'])
            html_template = 'user/email/admin_activate_acct.html'
            text_template = None
            send_message(to,context=context,subject=subject,html_template=html_template,text_template=text_template)
            
            return render_template('user/registration_success.html',success=success)
        else:
            flash("That registration request has expired")
            return redirect('/')

    if not request.form:
        pass
    else:
        if validForm(rec):
            #update the record
            user.update(rec,request.form)
            rec.active = 0 # Self registered accounts are inactive by default
            set_password_from_form(rec)
            set_username_from_form(rec)
            rec.access_token = get_access_token()
            rec.access_token_expires = time() + (3600 * 48)
            
            try:
                user.save(rec)
                
                #Send confirmation email to user
                full_name = '{} {}'.format(rec.first_name,rec.last_name).strip()
                to=[(full_name,rec.email)]
                context={'rec':rec,'confirmation_code':rec.access_token}
                subject = 'Signup Success'
                html_template = 'user/email/registration_confirm.html'
                text_template = 'user/email/registration_confirm.txt'
                send_message(to,context=context,subject=subject,html_template=html_template,text_template=text_template)
                
                #inform the admin
                to=[(app.config['MAIL_DEFAULT_SENDER'],app.config['MAIL_DEFAULT_ADDR'])]
                deleteURL = "{}://{}{}?delete={}".format(app.config['HOST_PROTOCOL'],app.config['HOST_NAME'],url_for('.delete'), rec.access_token)
                context={'rec':rec,'deleteURL':deleteURL,'registration_exp':datetime.fromtimestamp(rec.access_token_expires).strftime('%Y-%m-%d %H:%M:%S')}
                subject = 'Unconfirmed Account Request from - {}'.format(app.config['SITE_NAME'])
                html_template = 'user/email/admin_activate_acct.html'
                text_template = None
                send_message(to,context=context,subject=subject,html_template=html_template,text_template=text_template)

                g.db.commit()

            except Exception as e:
                g.db.rollback()
                mes = "An error occured while new user was attempting to register"
                printException(mes,"error",e)
                # Send email to the administrator
                to=[(app.config['MAIL_DEFAULT_SENDER'],app.config['MAIL_DEFAULT_ADDR'])]
                context={'mes':mes,'rec':rec,'e':str(e)}
                body = "Signup Error\n{{context.mes}}\n{{context.e}}\nrec:\n{{context.rec}}"
                send_message(to,context=context,body=body,subject=mes)
                success = False
            
            return render_template('user/registration_success.html',success=success)
        else:
            #validation failed
            user.update(rec,request.form)
            
    return render_template('user/user_edit.html', rec=rec, no_delete=no_delete, is_admin=is_admin, user_roles=user_roles, roles=roles, help=help)


@mod.route('/activate/', methods=['GET'])
@table_access_required(User)
def activate():
    """Allow administrator to activate a new user"""
    from takeabeltof.mailer import send_message
    
    activate = request.args.get('activate',None)
    if activate:
        user = User(g.db)
        rec=user.select_one(where='access_token = "{}"'.format(activate.strip()))
        if rec:
            rec.active = 1
            rec.access_token = None
            rec.access_token_expires = None
            user.save(rec)
            g.db.commit()
            
            # inform user that their account is now active
            full_name = '{} {}'.format(rec.first_name,rec.last_name).strip()
            to=[(full_name,rec.email)]
            context={'rec':rec,}
            subject = 'Account Activated'
            html_template = 'user/email/activation_complete.html'
            text_template = 'user/email/activation_complete.txt'
            send_message(to,context=context,subject=subject,html_template=html_template,text_template=text_template)
            
        else:
            flash("User not found with access_token: {}".format(activate))
            return redirect('/')
            
    else:
        flash("Activation code not in request args")
        return redirect('/')
    
    flash("New User Activation Successful")
    return edit(rec.id)
        
        
@mod.route('/delete', methods=['GET'])
@mod.route('/delete/', methods=['GET'])
@mod.route('/delete/<int:rec_id>/', methods=['GET'])
@table_access_required(User)
def delete(rec_id=None):
    setExits()
    delete_by_admin = request.args.get('delete',None)
    if delete_by_admin:
        user = User(g.db)
        rec=user.select_one(where='access_token = "{}"'.format(delete_by_admin.strip()))
        if rec:
            rec_id = rec.id
    
    if rec_id == None:
        rec_id = request.form.get('id',request.args.get('id',-1))
    
    rec_id = cleanRecordID(rec_id)
    if rec_id <=0:
        flash("That is not a valid record ID")
        return redirect(g.listURL)
        
    rec = User(g.db).get(rec_id,include_inactive=True)
    if not rec:
        flash("Record not found")
    else:
        User(g.db).delete(rec.id)
        g.db.commit()
        flash('User Record Deleted')
        
    return redirect(g.listURL)


def validForm(rec):
    # Validate the form
    goodForm = True
    user = User(g.db)
    
    if request.form['email'].strip() == '':
        goodForm = False
        flash('Email may not be blank')

    if request.form['email'].strip() != '' and not looksLikeEmailAddress(request.form['email'].strip()):
        goodForm = False
        flash("That doesn't look like a valid email address")

    if request.form['email'].strip() != '':
        found = user.get(request.form['email'].strip(),include_inactive=True)
        if found:
            if request.form['id'] == 'None' or found.id != int(request.form['id']):
                goodForm = False
                flash('That email address is already in use')
            
    # user name must be unique if supplied
    if 'new_username' in request.form:
        if request.form['new_username'].strip() != '':
            found = user.get(request.form['new_username'].strip(),include_inactive=True)
            if found:
                if request.form['id'] == 'None' or found.id != int(request.form['id']):
                    goodForm = False
                    flash('That User Name is already in use')
        
        if request.form["new_username"].strip() != '' and request.form["new_password"].strip() == '' and rec.password == '':
            goodForm = False
            flash('There must be a password if there is a User Name')
        
    if request.form["new_password"].strip() == '' and request.form["confirm_password"].strip() != '' and rec.password != '':
        goodForm = False
        flash("You can't enter a blank password.")
    
    #passwords must match if present
    if request.form['confirm_password'].strip() != request.form['new_password'].strip():
        goodForm = False
        flash('Passwords don\'t match.')
        
    return goodForm
    
def get_user_role_names(rec):
    user_roles = []
    roles = User(g.db).get_roles(rec.id)
    if roles:
        for x in roles:
            user_roles.append(x.name)
            
    return user_roles
    
def set_password_from_form(rec):
    if not request.form['new_password'] or (rec.password != None and request.form['new_password'].strip() == ''):
        # Don't change the password
        pass
    else:
        user_password = ''
        if request.form['new_password'].strip() != '':
            user_password = getPasswordHash(request.form['new_password'].strip())
            rec.access_token = None
            rec.access_token_expires = None

        if user_password != '':
            rec.password = user_password
        else:
            rec.password = None
    
def set_username_from_form(rec):
    user_name = ''
    if 'new_username' in request.form:
        user_name = request.form['new_username'].strip()
    
        if user_name != '':
            rec.username = user_name
        else:
            rec.username = None
    
