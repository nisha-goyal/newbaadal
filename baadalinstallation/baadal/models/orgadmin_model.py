# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    import gluon
    global auth; auth = gluon.tools.Auth()
    from gluon import db
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################


def get_all_orglevel_vm_list():
    
    users_of_same_org = db(db(auth.user.id == db.user.id).select(db.user.organisation_id).first()['organisation_id'] == db.user.organisation_id).select(db.user.id)

    
    vms = db(((db.vm_data.status == VM_STATUS_RUNNING) 
               | (db.vm_data.status == VM_STATUS_SUSPENDED) 
               | (db.vm_data.status == VM_STATUS_SHUTDOWN))
             & (db.user_vm_map.user_id.belongs(users_of_same_org))  
             & (db.user_vm_map.vm_id == db.vm_data.id)).select(db.vm_data.ALL)
    
    return get_hosted_vm_list(vms)
    


def get_verified_vm_list():

    users_of_same_org = db(auth.user.organisation_id == db.user.organisation_id).select(db.user.id)

    vms = db(((db.vm_data.status == VM_STATUS_VERIFIED) | (db.vm_data.status == VM_STATUS_APPROVED))
             & (db.vm_data.requester_id.belongs(users_of_same_org))).select(db.vm_data.ALL)

    return get_pending_vm_list(vms)
    
