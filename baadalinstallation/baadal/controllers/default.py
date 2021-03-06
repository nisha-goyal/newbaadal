# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import auth,request
###################################################################################

def user():
    """
    exposes:
    http://..../[app]/default/user/login 
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
    to decorate functions that need access control
	"""
    return dict(form=auth())


def index():
    return dict()

def contact():
    return dict()

def error():
    return dict(error=request.vars['error'])

def page_under_construction():
    return dict()
