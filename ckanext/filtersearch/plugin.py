try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.filtersearch import helpers
import pprint
import re
import json


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
    plugins.implements(plugins.IPackageController, inherit=True)
    #plugins.implements(plugins.IOrganizationController, inherit=True)
    #plugins.implements(plugins.IGroupController, inherit=True)



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
            'filtersearch_get_topic_field': helpers.filtersearch_get_topic_field,
            'filtersearch_get_bbox': helpers.filtersearch_get_bbox,
            'filtersearch_get_date_value': helpers.filtersearch_get_date_value,
            'filtersearch_check_resource_field': helpers.filtersearch_check_resource_field,
            'filtersearch_get_search_facets_from_fields': helpers.filtersearch_get_search_facets_from_fields
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
        #facets_dict.pop('author', None)

        # Add them
        #facets_dict['extras_iso_exTempStart'] = 'Temporal Extend Start'
        #facets_dict['extras_iso_exTempEnd'] = 'Temporal Extend End'
        #facets_dict['metadata_modified'] = 'Last modified'


        if self._topic_field:
            facets_dict[self._topic_field] = 'Categories'

        #print self._topic_field

        facets_dict['tags'] = 'Keywords'
        facets_dict['author'] = 'Authors'
        facets_dict['organization'] = 'Organizations'
        facets_dict['groups'] = 'Groups'
        facets_dict['license_id'] = 'Licenses'
        facets_dict['res_format'] = 'Formats'
        facets_dict['res_extras_par_model'] = 'Model'
        facets_dict['res_extras_par_experiment'] = 'Experiment'
        facets_dict['res_extras_par_frequency'] = 'Frequency'
        facets_dict['res_extras_par_variables'] = 'Variables'
        facets_dict['res_extras_par_ensemble'] = 'Ensemble'


        return facets_dict

    # IPackageController
    def after_search(self, search_results, search_params):
        #print("Params  -------------------------------------")
        #pprint.pprint(search_params)
        #print("Results -------------------------------------")
        #pprint.pprint(search_results)
        # Extract resource facet params from fq
        #print "after_search"
        #print search_results
        #print search_results['results']

        search_items = ["res_format", "res_extras_par_frequency", "res_extras_par_model", "res_extras_par_experiment","res_extras_par_variables","res_extras_par_ensemble"]
        package_text = ["format", "par_frequency", "par_model", "par_experiment","par_variables","par_ensemble" ]
        max_values_per_item = 40
        num_search_items = len (search_items)
        search_values = [[None for x in range(len(search_items))] for y in range(max_values_per_item)]


        fq = toolkit.get_or_bust(search_params, 'fq')
        #print (fq)

        if (fq[0].find('res_format') == -1) and (fq[0].find('par_') == -1):
            # Check versions and modify resource_list accordingly
            for pkg in search_results['results']:
                 resource_list = pkg['resources']
                 #print resource_list
                 new_resource_list = []
                 for resource in resource_list:
                     # Consider resource versions for Kathi; 27.6.17
                     #print resource
                     if 'newer_version' in resource:
                         #print "newer_version"
                         if resource['newer_version'] != '':
                              continue
                         else:
                             new_resource_list.append(resource)
                     else:
                         new_resource_list.append(resource)
                 pkg['resources'] = new_resource_list

            return search_results


        len_s = len(search_items)
        #print "otto"
        i = -1

        for item in search_items:
            i += 1
            if fq[0].find(search_items[i]) == -1:
                continue
            x = [m.start() for m in re.finditer(search_items[i], fq[0])]
            j = -1
            for val in x:
                j += 1
                tmp_str = fq[0][val:-1].split(' ')[0]
                tmp_str =  tmp_str.split(':')[1]
                if tmp_str.startswith('"') and tmp_str.endswith('"'):
                    tmp_str = tmp_str[1:-1]
                search_values[i][j] = tmp_str
                #print tmp_str

        #print search_values
        try:
              # Filter resources from package_search result :
              # logical or within one facet logical and across all facets
              #print search_results['results']
              for pkg in search_results['results']:
                  pkg['total_resources'] = len(pkg['resources'])
                  resource_list = pkg['resources']
                  new_resource_list = []
                  #print resource_list
                  for resource in resource_list:
                      # Consider resource versions for Kathi; 27.6.17
                      #print resource
                      if 'newer_version' in resource:
                          #print "newer_version"
                          if resource['newer_version'] != '':
                               pkg['total_resources'] -= 1
                               continue
                      num_matches = [False for x in range(num_search_items)]
                      for i in range(num_search_items):
                          #print search_values[i][0]
                          if search_values[i][0] == None:
                              #print "None Found: " + str(i)
                              num_matches[i] = True     # ie. parameter was not specified
                              continue
                          for j in range (len(search_values[i])):
                              if search_values[i][j] == None:
                                 break
                              #print resource
                              #print search_values[i][j]
                              #print resource.get(package_text[i])
                              #print resource.get('par_variables')
                              if resource.get(package_text[i]) == search_values[i][j]:
                                 num_matches[i] = True

                      append_resource = True
                      #print num_matches
                      for i in range (num_search_items):
                          if num_matches[i] == False:
                             append_resource = False

                      if append_resource:
                          new_resource_list.append(resource)

                  pkg['resources'] = new_resource_list


        except Exception as e:
            print("Exception: " + str(e))

        return search_results
