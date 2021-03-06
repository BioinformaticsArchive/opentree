# -*- coding: utf-8 -*-

#########################################################################
## Manages and manipulates studies in the Open Tree curation tool
## - index()    lists all studies in the system? or just mine?
## - create()   makes a new study (incl. one-time imports, etc)
## - edit()     manages an existing study
## - delete() 
## - validate() AJAX checks study against a remote validation service?
## - load()     AJAX call to load from remote store
## - store()    AJAX call to save to remote store
#########################################################################

from applications.opentree.modules.opentreewebapputil import(
    get_opentree_services_method_urls, 
    fetch_current_TNRS_context_names,
    get_maintenance_info)
# N.B. This module is shared with tree-browser app, which is aliased as
# 'opentree'. Any name changes will be needed here as well!

def index():
    """
    Show list searchable/filtered list of all studies
    (default filter = My Studies, if logged in?)
    """

    if auth.is_logged_in():
        # user is logged in, filter to their own studies by default?
        pass
    else:
        # anonymous visitor, show unfiltered list?
        pass

    return dict(message="study/index")


def view():
    """
    Allow any visitor to view (read-only!) a study on the 'master' branch

    ? OR can this include work-in-progress from a personal branch?
    """
    response.view = 'study/edit.html'
    view_dict = get_opentree_services_method_urls(request)
    view_dict['maintenance_info'] = get_maintenance_info(request)
    #view_dict['taxonSearchContextNames'] = fetch_current_TNRS_context_names(request)
    view_dict['studyID'] = request.args[0]
    view_dict['latestSynthesisSHA'] = _get_latest_synthesis_sha_for_study_id(view_dict['studyID'])
    view_dict['viewOrEdit'] = 'VIEW'
    view_dict['userCanEdit'] = auth.is_logged_in() and True or False;
    return view_dict

@auth.requires_login()
def create():
    # Block (redirect) if we've suspended study editing
    maintenance_info = get_maintenance_info(request)
    if maintenance_info.get('maintenance_in_progress', False):
        redirect(URL('curator', 'default', 'index', vars={"maintenance_notice":"true"}))
        pass
    view_dict = get_opentree_services_method_urls(request)
    view_dict['message'] = "study/create"
    return view_dict


@auth.requires_login()
def edit():
    # Block (redirect) if we've suspended study editing
    maintenance_info = get_maintenance_info(request)
    if maintenance_info.get('maintenance_in_progress', False):
        redirect(URL('curator', 'study', 'view', 
            vars={"maintenance_notice":"true"}, 
            args=request.args))
    # Fetch a fresh list of search contexts for TNRS? see working example in
    # the header search of the main opentree webapp
    view_dict = get_opentree_services_method_urls(request)
    view_dict['taxonSearchContextNames'] = fetch_current_TNRS_context_names(request)
    view_dict['studyID'] = request.args[0]
    view_dict['latestSynthesisSHA'] = _get_latest_synthesis_sha_for_study_id(view_dict['studyID'])
    view_dict['viewOrEdit'] = 'EDIT'
    return view_dict


def _get_latest_synthesis_sha_for_study_id( study_id ):
    # Fetch this SHA from treemachine. If not found in contributing studies, return None
    try:
        from gluon.tools import fetch
        import simplejson

        method_dict = get_opentree_services_method_urls(request)

        # fetch a list of all studies that contribute to synthesis
        fetch_url = method_dict['getSynthesisSourceList_url']
        if fetch_url.startswith('//'):
            # Prepend scheme to a scheme-relative URL
            fetch_url = "http:%s" % fetch_url
        # as usual, this needs to be a POST (pass empty fetch_args)
        source_list_response = fetch(fetch_url, data='')
        source_list = simplejson.loads( source_list_response )

        # split these source descriptions, which are in the form '{STUDY_ID_PREFIX}_{STUDY_NUMERIC_ID}_{TREE_ID}_{COMMIT_SHA}'
        contributing_study_info = { }   # store (unique) study IDs as keys, commit SHAs as values

        for source_desc in source_list:
            if source_desc == 'taxonomy':
                continue
            source_parts = source_desc.split('_')
            # add default prefix 'pg' to study ID, if not found
            if source_parts[0].isdigit():
                # prepend with default namespace 'pg'
                study_id = 'pg_%s' % source_parts[0]
            else:
                study_id = '_'.join(source_parts[0:2])
            if len(source_parts) == 4:
                commit_SHA_in_synthesis = source_parts[3]
            else:
                commit_SHA_in_synthesis = None
            contributing_study_info[ study_id ] = commit_SHA_in_synthesis

        return contributing_study_info.get( study_id, '')

    except Exception, e:
        # throw 403 or 500 or just leave it
        raise HTTP(500, T('Unable to retrieve latest synthesis SHA for study {u}'.format(u=study_id)))

@auth.requires_login()
def delete():
    return dict(message="study/delete")


@auth.requires_login()
def validate():
    return dict(message="study/validate")


@auth.requires_login()
def load():
    return dict(message="study/load")


@auth.requires_login()
def store():
    return dict(message="study/store")


