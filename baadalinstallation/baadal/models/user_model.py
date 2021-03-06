# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import db,auth,request
    import gluon
    global auth; auth = gluon.tools.Auth()
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from helper import is_moderator, is_faculty, get_vm_template_config
from auth_user import fetch_ldap_user, create_or_update_user

def get_my_pending_vm():
    vms = db(db.vm_data.status.belongs(VM_STATUS_REQUESTED, VM_STATUS_VERIFIED) 
             & (db.vm_data.requester_id==auth.user.id)).select(db.vm_data.ALL)

    return get_pending_vm_list(vms)


def get_my_hosted_vm():
    vms = db((db.vm_data.status > VM_STATUS_APPROVED) 
             & (db.vm_data.id==db.user_vm_map.vm_id) 
             & (db.user_vm_map.user_id==auth.user.id)).select(db.vm_data.ALL)

    return get_hosted_vm_list(vms)

#Create configuration dropdowns
def get_configuration_elem(form):
    
    xmldoc = get_vm_template_config() # Read vm_template_config.xml
    itemlist = xmldoc.getElementsByTagName('template')
    _id=0 #for default configurations set, select box id will be configuration_0 
    for item in itemlist:
        if item.attributes['default'].value != 'true': #if not default, get the id 
            _id=item.attributes['id'].value
        select=SELECT(_name='configuration_'+str(_id)) # create HTML select with name as configuration_id
        cfglist = item.getElementsByTagName('config')
        i=0
        for cfg in cfglist:
            #Create HTML options and insert into select
            select.insert(i,OPTION(cfg.attributes['display'].value,_value=cfg.attributes['value'].value))
            i+=1
        
        #Create HTML tr, and insert label and select box
        config_elem = TR(LABEL('Configuration:'),select,TD(),_id='config_row__'+str(_id))
        form[0].insert(2,config_elem)#insert tr element in the form

# Gets CPU, RAM and HDD information on the basis of template selected.
def set_configuration_elem(form):

    configVal = form.vars.configuration_0 #Default configuration dropdown
    template = form.vars.template_id
    
    # if configuration specific to selected template is available
    if eval('form.vars.configuration_'+str(template)) != None:
        configVal = eval('form.vars.configuration_'+str(template))

    configVal = configVal.split(',')
    
    form.vars.vCPU = int(configVal[0])
    form.vars.RAM = int(configVal[1])*1024
    form.vars.HDD = int(configVal[2])
    if form.vars.extra_HDD == None:
        form.vars.extra_HDD = 0


def validate_approver(form):
    faculty_user = request.post_vars.user_name
    faculty_user_name = request.post_vars.faculty_user
    
    if(faculty_user != ''):
        faculty_info = get_user_info(faculty_user, [FACULTY])
        if faculty_info[1] == faculty_user_name:
            form.vars.owner_id = faculty_info[0]
            form.vars.status = VM_STATUS_REQUESTED
            return
    
    faculty_info = get_user_info(faculty_user_name, [FACULTY])
    if faculty_info != None:
        form.vars.owner_id = faculty_info[0]
        form.vars.status = VM_STATUS_REQUESTED
    else:
        form.errors.faculty_user='Faculty Approver Username is not valid'


def request_vm_validation(form):
    set_configuration_elem(form)
    if not(is_moderator() | is_faculty()):
        validate_approver(form)
    else:
        form.vars.owner_id = auth.user.id
        form.vars.status = VM_STATUS_VERIFIED
    
    form.vars.requester_id = auth.user.id


def add_faculty_approver(form):

    _input=INPUT(_name='faculty_user',_id='faculty_user') # create INPUT
    _link = TD(A('Verify', _href='#',_onclick='verify_faculty()'))
    faculty_elem = TR(LABEL('Faculty Approver:'),_input,_link,_id='faculty_row')
    form[0].insert(-1,faculty_elem)#insert tr element in the form


def get_request_vm_form():
    
    form_fields = ['vm_name','template_id','extra_HDD','purpose']
    form_labels = {'vm_name':'Name of VM','extra_HDD':'Optional Additional Harddisk(GB)','template_id':'Template Image','purpose':'Purpose of this VM'}

    form =SQLFORM(db.vm_data, fields = form_fields, labels = form_labels, hidden=dict(user_name=''))
    get_configuration_elem(form) # Create dropdowns for configuration

    if not(is_moderator() | is_faculty()):
        add_faculty_approver(form)
    
    return form


def get_user_info(username, roles):
    user_query = db((db.user.username == username) 
             & (db.user.id == db.user_membership.user_id)
             & (db.user_membership.group_id == db.user_group.id)
             & (db.user_group.role.belongs(roles)))
    user = user_query.select().first()
    # If user not present in DB
    if not user:
        if current.auth_type == 'ldap':
            user_info = fetch_ldap_user(username)
            if user_info:
                if [obj for obj in roles if obj in user_info['roles']]:
                    create_or_update_user(user_info, False)
                    user = user_query.select().first()
    
    if user:
        return (user.user.id, (user.user.first_name + ' ' + user.user.last_name))	


def get_my_task_list(task_status, task_num):
    task_query = db((db.task_queue_event.status == task_status) 
                    & (db.task_queue_event.vm_id == db.vm_data.id) 
                    & (db.vm_data.requester_id==auth.user.id))

    events = task_query.select(db.task_queue_event.ALL, orderby = ~db.task_queue_event.start_time, limitby=(0,task_num))

    return get_task_list(events)

   
def get_vm_config(vm_id):

    vminfo = get_vm_info(vm_id)
    
    vm_info_map = {'id'              : str(vminfo.id),
                   'name'            : str(vminfo.vm_name),
                   'hdd'             : str(vminfo.HDD),
                   'extrahdd'        : str(vminfo.extra_HDD),
                   'ram'             : str(vminfo.RAM),
                   'vcpus'           : str(vminfo.vCPU),
                   'status'          : str(vminfo.status),
                   'ostype'          : 'Linux',
                   'purpose'         : str(vminfo.purpose),
                   'totalcost'       : str(vminfo.total_cost),
                   'currentrunlevel' : str(vminfo.current_run_level)}

    if is_moderator():
        vm_info_map.update({'host' : str(vminfo.host_id),
                             'vnc'  : str(vminfo.vnc_port)})

    return vm_info_map  
    
    
def get_vm_user_list(vm_id) :		
    vm_users = db((vm_id == db.user_vm_map.vm_id) & (db.user_vm_map.user_id == db.user.id)).select(db.user.ALL)
    user_id_lst = []
    for vm_user in vm_users:
        user_id_lst.append(vm_user)
    return user_id_lst

def check_snapshot_limit(vm_id):
    snapshots = len(db(db.snapshot.vm_id == vm_id).select())
    logger.debug("No of snapshots are " + str(snapshots))
    if snapshots < SNAPSHOTTING_LIMIT:
        return True
    else:
        return False

