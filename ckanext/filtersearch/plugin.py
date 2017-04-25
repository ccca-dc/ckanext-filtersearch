try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.filtersearch import helpers


def get_topic_field():
    # Get the value of the ckan.iauthfunctions.users_can_create_groups
    # setting from the CKAN config file as a string, or False if the setting
    # isn't in the config file.
    topic_field = config.get(
        'ckanext.filtersearch.topic_field', False)

    if topic_field:
        return 'extras_' + topic_field
    else:
        return None

class FiltersearchPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IFacets)
    plugins.implements(plugins.ITemplateHelpers)
    #plugins.implements(plugins.IRoutes, inherit=True)



    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'filtersearch')
        self._topic_field =  get_topic_field()

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'filtersearch_get_topic': helpers.filtersearch_get_topic,
            'filtersearch_get_items': helpers.filtersearch_get_items,
            'filtersearch_get_topic_field': helpers.filtersearch_get_topic_field
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

        # Add them
        #facets_dict['extras_iso_exTempStart'] = 'Temporal Extend Start'
        #facets_dict['extras_iso_exTempEnd'] = 'Temporal Extend End'
        #facets_dict['metadata_modified'] = 'Last modified'


        if self._topic_field:
            facets_dict[self._topic_field] = 'Topics'

        #print self._topic_field

        facets_dict['tags'] = 'Keywords'
        facets_dict['author'] = 'Authors'
        #facets_dict['groups'] = 'Groups'
        #facets_dict['organization'] = 'Organizations'
        facets_dict['res_format'] = 'Formats'
        facets_dict['license_id'] = 'Licenses'

        return facets_dict
