# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import auth,request,session
    import gluon
    global auth; auth = gluon.tools.Auth()
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from helper import is_moderator, is_faculty, is_orgadmin

@auth.requires_login()
@handle_exception
def request_vm():
    form = get_request_vm_form()
    
    # After validation, read selected configuration and set RAM, CPU and HDD accordingly
    if form.accepts(request.vars, session, onvalidation=request_vm_validation):
        logger.debug('VM requested successfully')
        redirect(URL(c='default', f='index'))
    return dict(form=form)

@auth.requires_login()
@handle_exception
def verify_faculty():

    username = request.vars.keywords
    faculty_info = get_user_info(username, [FACULTY])
    if faculty_info != None:
        return faculty_info[1]

@auth.requires_login()
@handle_exception
def list_my_vm():
    pending_vm = get_my_pending_vm()
    hosted_vm = get_my_hosted_vm()        
    
    return dict(pending_vm = pending_vm, hosted_vm = hosted_vm)


@auth.requires_login()
@handle_exception
def settings():

    vm_id=request.args[0]
    vm_users = None
    vm_info = get_vm_config(vm_id)
    
    if is_moderator() | is_faculty() | is_orgadmin():
        vm_users = get_vm_user_list(vm_id)
    
    vm_operations = get_vm_operations(vm_id)

    vm_snapshots = get_vm_snapshots(vm_id)
    
    return dict(vminfo = vm_info , vmoperations = vm_operations, vmsnapshots = vm_snapshots, vmusers = vm_users)     


@auth.requires_login()
@handle_exception
def start_machine():
    vm_id=request.args[0]       
    add_vm_task_to_queue(vm_id,TASK_TYPE_START_VM)
    redirect_list_vm()


@auth.requires_login()
@handle_exception
def shutdown_machine():
    vm_id=request.args[0]      
    add_vm_task_to_queue(vm_id,TASK_TYPE_STOP_VM)        
    redirect_list_vm()


@auth.requires_login()
@handle_exception
def destroy_machine():
    vm_id=request.args[0]       
    add_vm_task_to_queue(vm_id,TASK_TYPE_DESTROY_VM)        
    redirect_list_vm()


@auth.requires_login()
@handle_exception       
def resume_machine():
    vm_id=request.args[0]     
    add_vm_task_to_queue(vm_id,TASK_TYPE_RESUME_VM)        
    redirect_list_vm()


@auth.requires_login()
@handle_exception       
def delete_machine():
    vm_id = request.args[0]      
    add_vm_task_to_queue(vm_id,TASK_TYPE_DELETE_VM)        
    redirect_list_vm()


@auth.requires_login()
@handle_exception       
def pause_machine():
    vm_id=request.args[0]  
    add_vm_task_to_queue(vm_id,TASK_TYPE_SUSPEND_VM)        
    redirect_list_vm()

@auth.requires_login()
@handle_exception       
def adjrunlevel():
    #Adjust the run level of the virtual machine
    vm_id=request.args[0]
    vminfo = get_vm_config(vm_id)        
    return dict(vm=vminfo)

@auth.requires_login()
def clonevm():    
    session.flash="Has to be implemented"

@auth.requires_login()
@handle_exception       
def changelevel():
    vm_id=request.args[0]     
    add_vm_task_to_queue(vm_id,TASK_TYPE_CHANGELEVEL_VM)        
    redirect_list_vm()

@auth.requires_login()
@handle_exception       
def snapshot():
    vm_id = int(request.args[0])
   
    if check_snapshot_limit(vm_id):
        add_vm_task_to_queue(vm_id,TASK_TYPE_SNAPSHOT_VM)
        session.flash = "Your VM snapshoting request has been queued"
        redirect_list_vm()
    else:
        session.flash = "Snapshot Limit Reached. Delete Previous Snapshots to take new snapshot."

@auth.requires_login()
@handle_exception
def delete_snapshot():
    vm_id = int(request.args[0])
    snapshot_id = int(request.args[1])
    add_vm_task_to_queue(vm_id, TASK_TYPE_DELETE_SNAPSHOT, None, None, None, snapshot_id)
    session.flash = "Your delete snapshot request has been queued"
    redirect_list_vm()

@auth.requires_login()
@handle_exception
def revert_to_snapshot():
    vm_id = int(request.args[0])
    snapshot_id = int(request.args[1])
    add_vm_task_to_queue(vm_id, TASK_TYPE_REVERT_TO_SNAPSHOT, None, None, None, snapshot_id)
    session.flash = "Your revert to snapshot request has been queued"
    redirect_list_vm()

@auth.requires_login()
@handle_exception       
def list_my_task():
    form = get_task_num_form()
    task_num = ITEMS_PER_PAGE
    form.vars.task_num = task_num

    if form.accepts(request.vars, session, keepvalues=True):
        task_num = int(form.vars.task_num)
    
    pending = get_my_task_list(TASK_QUEUE_STATUS_PENDING, task_num)
    success = get_my_task_list(TASK_QUEUE_STATUS_SUCCESS, task_num)
    failed = get_my_task_list(TASK_QUEUE_STATUS_FAILED, task_num)

    return dict(pending=pending, success=success, failed=failed, form=form)  


def redirect_list_vm():
    if (session.prev_url != None):
        redirect(URL(r=request,f=session.prev_url))
    else :
        redirect(URL(r=request,c='user',f='list_my_vm'))
        
