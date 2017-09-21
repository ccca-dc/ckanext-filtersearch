try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config

import re
import datetime
import pytz

from pylons import config
from pylons.i18n import gettext

import json
import ckan.logic as logic
get_action = logic.get_action

import ckan.plugins.toolkit as tk
context = tk.c
import ckan.lib.base as base
Base_c = base.c
from pylons import c
import logging
log = logging.getLogger(__name__)
import random
from ckanext.scheming import helpers as hs
import pprint # Pretty Print oif dicts :-)
import ckan.lib.helpers as h
import json

# Potentially for version 2.7 - Kathi
from webhelpers.text import truncate as ckan_truncate

from ckan.common import (
    _, ungettext, g, c, request, session, json, OrderedDict
)

def filtersearch_snippet(template_name, **kw):
    ''' Copied from CKAN
    This function is used to load html snippets into pages. keywords
    can be used to pass parameters into the snippet rendering '''
    import ckan.lib.base as base
    #print ("***************Anja ckan helper snippe")
    #print(template_name)
    #print (kw)
    return base.render_snippet(template_name, **kw)

def filtersearch_toggle_following(obj_type, obj_id):
    ''' Modified from CKAN - Anja 20.9.17
    Return a follow button for the given object type and id.

    If the user is not logged in return an empty string instead.

    :param obj_type: the type of the object to be followed when the follow
        button is clicked, e.g. 'user' or 'dataset'
    :type obj_type: string
    :param obj_id: the id of the object to be followed when the follow button
        is clicked
    :type obj_id: string

    :returns: a follow button as an HTML snippet
    :rtype: string

    '''
    obj_type = obj_type.lower()
    if obj_type != 'dataset':
        return ''
    # If the user is logged in show the follow/unfollow button
    if c.user:
        #print c
        #context = {'model': model, 'session': model.Session, 'user': c.user}
        context = {'user': c.user}
        action = 'am_following_dataset'
        following = logic.get_action(action)(context, {'id': obj_id})
        return filtersearch_snippet('snippets/filtersearch_follow_button.html',
                       following=following,
                       obj_id=obj_id,
                       obj_type=obj_type)
    return ''

def filtersearch_get_search_facets_from_fields(m_facets,fields):
    #print "********+ Filter search helper"
    #print fields
    #print m_facets

    s_f = {f[0]:[f[1]] for f in fields}

    for f in fields:
        #print f[0]
        #print f[1]
        #print s_f[f[0]]
        if f[1] not in s_f[f[0]]:
            s_f[f[0]].append(f[1])

    if m_facets:
        m_facets['fields'] = s_f
    #print m_facets
    #for value in m_facets[fields]:
        #print value

    #result = json.dumps(m_facets)
    #print m_facets

    return m_facets

def filtersearch_check_resource_field(field):
    ' fields see plugin.py after_search'
    search_items = ["res_format", "res_extras_par_frequency", "res_extras_par_model", "res_extras_par_experiment","res_extras_par_variables","res_extras_par_ensemble"]
    if field in search_items:
        return True
    else:
        return False

def filtersearch_get_topic_field():
    topic_field = config.get(
        'ckanext.filtersearch.topic_field', False)

    if topic_field:
        return 'extras_' + topic_field
    else:
        return None

def filtersearch_get_items(facet,extras):

     items = h.get_facet_items_dict(facet,0) # 0 is important! means alqway get all ...
     #if facet == "par_experiment":
        # print  json.dumps(items)

     if facet == filtersearch_get_topic_field():
         for x in items:
             x['href'] = h.remove_url_param(facet, x['name'],extras=extras) if x['active'] else h.add_url_param(new_params={facet: x['name']},extras=extras)
             x['label'] = filtersearch_get_topic(facet, x['name'])
             x['display_name'] = filtersearch_get_topic(facet, x['name'])
             x['label_truncated'] =ckan_truncate(x['label'], 22)
             x['count'] = ('(%d)' % x['count'])
             x['a'] = "true" if x['active'] else None # Angular needs it this way :-)
             x['title'] = x['label']

     elif facet == "res_extras_par_frequency":
         for x in items:
              x['href'] = h.remove_url_param(facet, x['name'], extras=extras) if x['active'] else h.add_url_param(new_params={facet: x['name']},extras=extras)
              x['label'] =  x['display_name']
              x['label_truncated'] = ckan_truncate(x['label'], 22)
              x['count'] = ('(%d)' % x['count'])
              x['a'] = "true" if x['active'] else None # Angular needs it this way :-)
              if x['label'] == "son":
                  x['title'] = "September/Oktober/November"
              elif x['label'] == "mam":
                  x['title'] = "M\xc3\xa4rz/April/Mai"
              elif x['label'] == "jja":
                  x['title'] = "Juni/Juli/August"
              elif x['label'] == "djf":
                  x['title'] = "Dezember/Januar/Februar"
              else:
                  x['title'] = x['label']
     else:
         for x in items:
             x['href'] = h.remove_url_param(facet, x['name'], extras=extras) if x['active'] else h.add_url_param(new_params={facet: x['name']},extras=extras)
             x['label'] =  x['display_name']
             x['label_truncated'] = ckan_truncate(x['label'], 22)
             x['count'] = ('(%d)' % x['count'])
             x['a'] = "true" if x['active'] else None # Angular needs it this way :-)
             x['title'] = x['label']


    # remove unicode .... only by dumping to json ...
     result = json.dumps(items)
     return result

def filtersearch_get_resource_items(facet,extras):
    # for resources filters on a single package - OEKS15!!!!!!!!!!!! Anja, 27.7.17
     #print "************* Anja"
     items = h.get_facet_items_dict(facet,0) # 0 is important! means always get all ...
     if facet == "res_extras_par_frequency":
         for x in items:
              x['href'] = h.remove_url_param(facet, x['name'], extras=extras) if x['active'] else h.add_url_param(new_params={facet: x['name']},extras=extras)
              x['label'] =  x['display_name']
              x['label_truncated'] = ckan_truncate(x['label'], 22)
              #x['count'] = ('(%d)' % x['count'])
              x['count'] = ('') # just one package
              x['a'] = "true" if x['active'] else None # Angular needs it this way :-)
              if x['label'] == "son":
                  x['title'] = "September/Oktober/November"
              elif x['label'] == "mam":
                  x['title'] = "M\xc3\xa4rz/April/Mai"
              elif x['label'] == "jja":
                  x['title'] = "Juni/Juli/August"
              elif x['label'] == "djf":
                  x['title'] = "Dezember/Januar/Februar"
              else:
                  x['title'] = x['label']

     else:
         for x in items:
             x['href'] = h.remove_url_param(facet, x['name'], extras=extras) if x['active'] else h.add_url_param(new_params={facet: x['name']},extras=extras)
             x['label'] =  x['display_name']
             x['label_truncated'] = ckan_truncate(x['label'], 22)
             #x['count'] = ('(%d)' % x['count'])
             x['count'] = ('') # just one package
             x['a'] = "true" if x['active'] else None # Angular needs it this way :-)
             x['title'] = x['label']


    # remove unicode .... only by dumping to json ...
     result = json.dumps(items)
     return result

def filtersearch_get_topic(field, value):
    #print "#####################################"
    schema = hs.scheming_dataset_schemas(False)
    if not schema:
        return value
    d_schema = schema['dataset']
    #pprint.pprint(d_schema['dataset_fields'])
    if not d_schema:
        return value
    if field.startswith('extras_'):
        real_field = field.split('_',1)[1]
    else:
        real_field = field
    f_schema = hs.scheming_field_by_name(d_schema['dataset_fields'], real_field)
    if not f_schema:
        return value
    #pprint.pprint(f_schema)
    result = hs.scheming_choices_label(f_schema['choices'], value)
    if not result:
        return value
    #print result
    return result

def filtersearch_get_bbox(query_string):

    q_field = 'ext_bbox'

    index = query_string.find(q_field)

    if index == -1:
        return ""

    mystring = query_string.split(q_field)

    if len (mystring) < 2:
        return ""

    if len (mystring[1]) < 2:
        return ""

    if  mystring[1][1] == '&':   #means empty, .i.e. not set'
        return ""
    else:
        return "true"

def filtersearch_get_date_value(query_string, q_field):


    index = query_string.find(q_field)

    if index == -1:
        return ""

    mystring = query_string.split(q_field)

    if len (mystring) < 2:
        return ""

    return_value = mystring[1][1:5]

    if len (return_value) < 2:
        return ""

    if return_value[0] == '&':
        return ""
    else:
        return return_value
