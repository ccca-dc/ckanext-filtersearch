import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.filtersearch import helpers


class FiltersearchPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IFacets)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes, inherit=True)


    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'filtersearch')

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'filtersearch_get_topic': helpers.filtersearch_get_topic,
            'filtersearch_get_items': helpers.filtersearch_get_items
        }
    # IFacets

    def dataset_facets(self, facets_dict, package_type):
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
        facets_dict['extras_iso_tpCat'] = 'Topics'
        facets_dict['tags'] = 'Keywords'
        facets_dict['author'] = 'Authors'
        facets_dict['groups'] = 'Groups'
        facets_dict['organization'] = 'Organizations'
        facets_dict['res_format'] = 'Formats'
        facets_dict['license_id'] = 'Licenses'

        return facets_dict
