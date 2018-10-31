from flask import request, session, g, redirect, url_for, \
     render_template, flash, Blueprint
from users.models import Role
from takeabeltof.utils import printException, cleanRecordID
from users.admin import login_required, table_access_required

mod = Blueprint('role',__name__, template_folder='../templates', url_prefix='/role')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.edit')
    g.deleteURL = url_for('.delete')
    g.title = 'Role'

@mod.route('/')
@table_access_required(Role)
def display():
    setExits()
    # get all records
    recs = Role(g.db).select()
    return render_template('role/role_list.html',recs=recs)
    

## Edit the role
@mod.route('/edit', methods=['POST', 'GET'])
@mod.route('/edit/', methods=['POST', 'GET'])
@mod.route('/edit/<int:rec_id>/', methods=['POST','GET'])
@table_access_required(Role)
def edit(rec_id=None):
    setExits()

    role = Role(g.db)
    rec = None
    
    if rec_id == None:
        rec_id = request.form.get('id',request.args.get('id',-1))
        
    rec_id = cleanRecordID(rec_id)
    #import pdb;pdb.set_trace

    if rec_id < 0:
        flash("That is not a valid ID")
        return redirect(g.listURL)
        
    if not request.form:
        """ if no form object, send the form page """
        if rec_id == 0:
            rec = role.new()
        else:
            rec = role.get(rec_id)
            if not rec:
                flash("Unable to locate that record")
                return redirect(g.listURL)
    else:
        #have the request form
        #import pdb;pdb.set_trace()
        if rec_id and request.form['id'] != 'None':
            rec = role.get(rec_id)
        else:
            # its a new unsaved record
            rec = role.new()
            role.update(rec,request.form)

        if validForm(rec):
            #update the record
            role.update(rec,request.form)
            # make names lower case
            rec.name=request.form['name'].lower().strip()
                        
            try:
                role.save(rec)
                g.db.commit()
            except Exception as e:
                g.db.rollback()
                flash(printException('Error attempting to save '+g.title+' record.',"error",e))

            return redirect(g.listURL)
        
        else:
            # form did not validate
            pass

    # display form
    return render_template('role/role_edit.html', rec=rec)
    

@mod.route('/delete/', methods=['GET','POST'])
@mod.route('/delete/<int:rec_id>/', methods=['GET','POST'])
@table_access_required(Role)
def delete(rec_id=None):
    setExits()
    if rec_id == None:
        rec_id = request.form.get('id',request.args.get('id',-1))
    
    rec_id = cleanRecordID(rec_id)
    if rec_id <=0:
        flash("That is not a valid record ID")
        return redirect(g.listURL)
        
    rec = Role(g.db).get(rec_id)
    if not rec:
        flash("Record not found")
    else:
        Role(g.db).delete(rec.id)
        g.db.commit()
        
    return redirect(g.listURL)

    
def validForm(rec):
    # Validate the form
    goodForm = True
    
    if request.form['name'].strip() == '':
        goodForm = False
        flash('Name may not be blank')
    else:
        # name must be unique (but not case sensitive)
        where = 'lower(name)="{}"'.format(request.form['name'].lower().strip(),)
        if rec.id:
            where += ' and id <> {}'.format(rec.id)
        if Role(g.db).select(
            where=where
            ) != None:
            goodForm = False
            flash('Role names must be unique')
        
    # Rank must be in a reasonalble range
    temp_rank = cleanRecordID(request.form['rank'])
    if temp_rank < 0 or temp_rank > 1000:
        goodForm = False
        flash("The Rank must be between 0 and 1000")
        
    return goodForm
    

