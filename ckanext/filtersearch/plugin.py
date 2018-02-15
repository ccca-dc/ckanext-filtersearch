try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.filtersearch import helpers
from ckanext.resourceversions import helpers as hres
import pprint
import re
import json
from ckan.common import OrderedDict, c, g, request, _
from ckan import model
import ckan.logic as logic

from paste.deploy.converters import asbool
import ast
import collections

import  ckan.plugins.toolkit as tk
context = tk.c


class FiltersearchPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IFacets)
    plugins.implements(plugins.IPackageController, inherit=True)
    #plugins.implements(plugins.IOrganizationController, inherit=True)
    #plugins.implements(plugins.IGroupController, inherit=True)



    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'filtersearch')

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'filtersearch_get_topic': helpers.filtersearch_get_topic,
            'filtersearch_get_items': helpers.filtersearch_get_items,
            'filtersearch_get_resource_items': helpers.filtersearch_get_resource_items,
            'filtersearch_get_bbox': helpers.filtersearch_get_bbox,
            'filtersearch_get_date_value': helpers.filtersearch_get_date_value,
            'filtersearch_get_search_facets_from_fields': helpers.filtersearch_get_search_facets_from_fields,
            'filtersearch_toggle_following': helpers.filtersearch_toggle_following,
            'filtersearch_get_fixed_facets': helpers.filtersearch_get_fixed_facets,
            'filtersearch_get_facet_specific_count': helpers.filtersearch_get_facet_specific_count,
        }

    def topic_field (self):
        return self._topic_field

    # IFacets
    def dataset_facets(self, facets_dict, package_type):
        return self._facets(facets_dict)
    def group_facets(self, facets_dict, group_type, package_type):
        return self._facets(facets_dict)
    def organization_facets(self, facets_dict, organization_type, package_type):
        return self._facets(facets_dict)

    def _facets(self, facets_dict):

        # Reorder facets

        # Delete facets
        facets_dict.pop('organization', None)
        facets_dict.pop('license_id', None)
        facets_dict.pop('res_format', None)
        facets_dict.pop('groups', None)
        facets_dict.pop('tags', None)
        facets_dict.pop('author', None)

        #Add them again
        facets_dict['tags'] = 'Keywords'
        facets_dict['author'] = 'Authors'
        facets_dict['organization'] = 'Organizations'
        facets_dict['license_id'] = 'Licenses'
        facets_dict['groups'] = 'Groups'


        #Add frequency
        facets_dict['frequency'] = 'Frequency'

        # Get specifc field names for facetting
        #data_dict={'sort': None, 'fq': '', 'rows': 1, 'facet.field': [ 'extras_specifics' ], 'q': u'', 'start': 0, 'extras': {}}
        #data_dict={'sort': None, 'fq': '', 'facet.field': [ 'extras_specifics' ],'q': u''}
        #data_dict={'sort': None, 'fq': '+dataset_type:dataset','q': u'extras_specifics:[\'\' TO *]'}
        data_dict={'sort': None, 'fq': '+dataset_type:dataset','q': u'extras_specifics:*'}

        query = tk.get_action('package_search')({}, data_dict)

        facet_list =[]
        for x in query['results']:
            for y in x['specifics']:
                facet_name = 'extras_specifics_' + y['name']
                if not any(facet_name in f['name'] for f in facet_list):
                    f = {}
                    f['name'] = facet_name
                    f['value'] = y['name']
                    f['count'] = 1
                    facet_list.append(f)
                else:
                    # count in order to check whether the the facet should be added - ini -parameter
                    for f in facet_list:
                        if f['name'] == facet_name:
                            f['count'] = f['count'] + 1


        #Add them if we have enough datastes with respective values
        num = helpers.filtersearch_get_facet_specific_count();

        for x in facet_list:
            if x['count'] >= num:
                facets_dict[x['name']] = x['value']

        print facet_list

        # Add Variables:
        facets_dict['extras_specifics_Variables'] = 'Variables'

        #Add formats
        facets_dict['res_format'] = 'Formats'

        return facets_dict
