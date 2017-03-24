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
import ckan.lib.formatters as formatters



def filtersearch_get_topic(field, value):

    print  (value)
    print field
    print c.pkg_dict
    

    if value is "001":
        return 'farming'
    elif value is "002":
        return 'biota'
    elif value is "003":
        return 'boundaries'
    elif value is "004":
        return 'climatology, meteorology, atmosphere'
    elif value is "005":
        return 'economy'
    elif value is "006":
        return 'elevation'
    elif value is "007":
        return 'environment'
    elif value is "008":
        return 'geoscientific information"'
    elif value is "009":
        return 'health'
    elif value is "010":
        return 'imagery, basemaps, earth cover'
    elif value is "011":
        return 'intelligence military'
    elif value is "012":
        return 'inland waters'
    elif value is "013":
        return 'location'
    elif value is "014":
        return 'oceans'
    elif value is "015":
        return 'planning cadastre'
    elif value is "016":
        return 'society'
    elif value is "017":
        return 'structure'
    elif value is "018":
        return 'transportation'
    elif value is "019":
        return 'utilities communication'
    else:
        return value
