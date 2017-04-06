import re
import datetime
import pytz

from pylons import config
from pylons.i18n import gettext

import json
import ckan.logic as logic
get_action = logic.get_action


import  ckan.plugins.toolkit as tk
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


from ckan.common import (
    _, ungettext, g, c, request, session, json, OrderedDict
)

def filtersearch_get_items(facet):
     items = h.get_facet_items_dict(facet,0) # = means alqway get all ...
     #print ("************************************************Anja")
     for x in items:
         x['href'] = h.remove_url_param(facet, x['name']) if x['active'] else h.add_url_param(new_params={facet: x['name']})
         x['label'] = filtersearch_get_topic(facet, x['name'])  if facet == "extras_iso_tpCat" else x['display_name']
         x['label_truncated'] = h.truncate(x['label'], 22) if facet != "extras_iso_tpCat" else x['label']
         x['count'] = ('(%d)' % x['count'])
         x['a'] = "true" if x['active'] else None # Angular needs it this way :-)

    # remove unicode ....

     #print ("Anja ---- No of Items: " + str(len(items)))
     for item in items:
         for k, v in item.iteritems():
        #    print (k +": " + str(item[k]))
            try:
                item[k] = v.encode('utf-8')
            except:
                continue

    #item = dict((str(k), str(v)) for k, v in item.items())


     return items

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
