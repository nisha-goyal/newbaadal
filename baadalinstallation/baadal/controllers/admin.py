# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import request,response,session
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################

@check_moderator
@handle_exception
def list_all_vm():
    vm_list = get_all_vm_list()
    return dict(vmlist = vm_list)

@check_moderator
@handle_exception
def hosts_vms():
    hostvmlist = get_vm_groupby_hosts()        
    return dict(hostvmlist = hostvmlist)

@check_moderator
@handle_exception
def add_template():
    form = get_add_template_form()
    return dict(form = form)

@check_moderator
@handle_exception
def host_details():
    hosts = get_all_hosts()

    form=get_search_host_form()
    if form.accepts(request.vars,session):
        session.flash='Check the details'
        redirect(URL(c='admin', f='add_host',args=form.vars.host_ip))
    elif form.errors:
        session.flash='Error in form'
        
    return dict(form=form,hosts=hosts)   

@check_moderator
@handle_exception
def add_host():
    if_redirect = False
    host_ip = request.args[0]
    form = get_host_form(host_ip)
    if form.accepts(request.vars,session):
        session.flash='New Host added'
        if_redirect = True
    elif form.errors:
        session.flash='Error in form'
    if if_redirect :
        redirect(URL(c='admin', f='host_details'))
    else :
        return dict(form=form)

@check_moderator
@handle_exception
def add_datastore():
    form = get_add_datastore_form()
    return dict(form=form)

@check_moderator
@handle_exception
def user_details():
    vm_id = request.args[0]
    form = get_search_user_form()
    if form.accepts(request.vars, session, onvalidation = validate_user):
        redirect(URL(c ='admin', f = 'add_user_to_vm', args = [form.vars.user_id, vm_id]))
    elif form.errors:
        session.form = 'Invalid user id'

    return dict(form=form)

@check_moderator
@handle_exception
def add_user_to_vm():
    username = request.args[0]
    vm_id = request.args[1]
    form = get_user_form(username, vm_id)

    if form.accepts(request.vars,session):
        add_user_vm_access(vm_id, form.vars.user_id)
        session.flash = "User is added to vm"
        redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))
    elif form.errors:
        session.form = 'Error in form'
    return dict(form = form)

@check_moderator
@handle_exception
def delete_user_vm():
    vm_id=request.args[0]
    user_id=request.args[1]
    delete_user_vm_access(vm_id,user_id)    			
    session.flash = 'User access is eradicated.'
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@check_moderator
@handle_exception
def migrate_vm():

    if_redirect = False
    vm_id = request.args[0]
    form = get_migrate_vm_form(vm_id)

    if form.accepts(request.vars,session,keepvalues = True):

        migrate_vm = True

        if form.vars.live_migration == None:
            if is_vm_running(vm_id):
                response.flash = "Your VM is already running. Kindly turn it off and then retry!!!"
                migrate_vm = False

        if migrate_vm:
            add_vm_task_to_queue(vm_id, TASK_TYPE_MIGRATE_VM, form.vars.destination_host, form.vars.live_migration )
            session.flash = 'Your task has been queued. Please check your task list for status.'
            if_redirect = True

    elif form.errors:
        response.flash = 'Error in form'

    if if_redirect :
        redirect(URL(c = 'admin', f = 'hosts_vms'))
    return dict(form=form)
    
@check_moderator
@handle_exception
def lockvm():
    vm_id=request.args[0]
    vminfo=get_vm_info(vm_id)
    if(not vminfo.locked):
        add_vm_task_to_queue(vm_id, TASK_TYPE_DESTROY_VM)
        session.flash = "VM will be force Shutoff and locked. Check the task queue."
        update_vm_lock(vm_id,True)
    else:
        update_vm_lock(vm_id,False)
        session.flash = "Lock Released. Start VM yourself."
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@check_moderator
@handle_exception
def task_list():

    form = get_task_num_form()
    task_num = ITEMS_PER_PAGE
    form.vars.task_num = task_num

    if form.accepts(request.vars, session, keepvalues=True):
        task_num = int(form.vars.task_num)
    
    pending = get_task_by_status(TASK_QUEUE_STATUS_PENDING, task_num)
    success = get_task_by_status(TASK_QUEUE_STATUS_SUCCESS, task_num)
    failed = get_task_by_status(TASK_QUEUE_STATUS_FAILED, task_num)
    
    return dict(pending=pending, success=success, failed=failed, form=form)

@check_moderator
@handle_exception
def ignore_task():
    task_id=request.args[0]
    update_task_ignore(task_id)
    
    redirect(URL(r=request,c='admin',f='task_list'))

@check_moderator
@handle_exception
def retry_task():
    task_id=request.args[0]
    update_task_retry(task_id)
    
    redirect(URL(r=request,c='admin',f='task_list'))

@check_moderator
@handle_exception
def delete_machine():   
    vm_id=request.args[0]
    add_vm_task_to_queue(vm_id,TASK_TYPE_DELETE_VM)    

    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@check_moderator
@handle_exception
def edit_vmconfig():

    vm_id = int(request.args[0])  
    vm_info = get_vm_config(vm_id)

    form = get_edit_vm_config_form(vm_info)

    form.vars.vmname = request.args[0]

    if form.accepts(request.vars, session):
        if int(vm_info['status']) == VM_STATUS_SHUTDOWN:
            updated_vm_config = {'ram' : form.vars.ram, 'vcpus' : form.vars.vcpus}
            add_vm_task_to_queue(vm_id, TASK_TYPE_EDITCONFIG_VM, None, None, updated_vm_config)
            session.flash = "Your request has been queued!!!"
        else:
            session.flash='VM is not Off. Turn it off first'

        redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

    return dict(form=form)

@check_moderator
def mailToGUI():
    session.flash="Has to be implemented"


@check_moderator
def add_disk():
    session.flash="Has to be implemented"

@check_moderator
def sanity_check():
    output = check_sanity()
    return dict(vms=output)
    
@check_moderator
def sync_vm():
    task = request.args[0]
    vm_name = request.args[1]
    host_id = request.args[2]
    if task == 'Delete_Orphan':
        delete_orhan_vm(vm_name, host_id)
    elif task == 'Add_Orphan':
        add_orhan_vm(vm_name, host_id)
    elif task == 'Delete_VM_Info':
        delete_vm_info(vm_name)
    redirect(URL(r=request,c='admin',f='sanity_check'))

