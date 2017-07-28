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
from ckan.common import OrderedDict, c, g, request, _
from ckan import model
import ckan.logic as logic

from paste.deploy.converters import asbool
import ast
import collections


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
        self._topic_field =  get_topic_field()

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'filtersearch_get_topic': helpers.filtersearch_get_topic,
            'filtersearch_get_items': helpers.filtersearch_get_items,
            'filtersearch_get_resource_items': helpers.filtersearch_get_resource_items,
            'filtersearch_get_topic_field': helpers.filtersearch_get_topic_field,
            'filtersearch_get_bbox': helpers.filtersearch_get_bbox,
            'filtersearch_get_date_value': helpers.filtersearch_get_date_value,
            'filtersearch_check_resource_field': helpers.filtersearch_check_resource_field,
            'filtersearch_get_search_facets_from_fields': helpers.filtersearch_get_search_facets_from_fields
        }

    def topic_field (self):
        return self._topic_field

    # IRoutes
    def before_map(self, map):
        map.connect('dataset_read', '/dataset/{id}',
                    controller ='ckanext.filtersearch.controllers.read:ReadController', action='read',
                    ckan_icon='sitemap')
        return map

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

    #copied from ckan
    def _update_facet_titles(self, facets, package_type):
        for plugin in plugins.PluginImplementations(plugins.IFacets):
            facets = plugin.dataset_facets(
                facets, package_type, None)
    #copied from ckan
    def _guess_package_type(self, expecting_name=False):
        """
            Guess the type of package from the URL handling the case
            where there is a prefix on the URL (such as /data/package)
        """

        # Special case: if the rot URL '/' has been redirected to the package
        # controller (e.g. by an IRoutes extension) then there's nothing to do
        # here.
        if request.path == '/':
            return 'dataset'

        parts = [x for x in request.path.split('/') if x]

        idx = -1
        if expecting_name:
            idx = -2

        pt = parts[idx]
        if pt == 'package':
            pt = 'dataset'

        return pt



    # IPackageController
    def before_view(self, data_dict):
         print "**********************before_view filtersearch"
         print "**********************before_view filtersearch end"

         return data_dict

         #print c
         facets = OrderedDict()
         temp_facets = None
         search_url_params = None

         for k,v in request.params.items():
             #
             print "***************"
             print k
             print v
             print "***************"
             if k=='facets':
                 print type(v)
                 temp_facets = eval(v.encode('utf-8'))
             if k=='search_url_params':
                 search_url_params = v

         if temp_facets:
             facets = collections.OrderedDict(temp_facets)

         for x in facets:
             if not x.startswith ('res_'):
                 facets.pop(x)
             else:
                  print x
         c.facets = facets
         c.search_url_params = search_url_params
         print type(facets)
         #print c.facets
         #print type(search_url_params)

         #d = eval(facets)
         #d = ast.literal_eval(facets)

         #print d
         #print type(d)
         #c.facets = d


         return data_dict

         q = c.q = request.params.get('q', u'')

         print q
         #print request.params.items['facets']
         #print request
         print request.urlvars
         #print request.urlargs
         #print request.body

         #if c.search_url_params:
             #fq = toolkit.get_or_bust(c.search_url_params, 'fq')
             #print (fq)


         ###############################################
         #### from search.py
         package_type = self._guess_package_type()

         c.fields = []
         # c.fields_grouped will contain a dict of params containing
         # a list of values eg {'tags':['tag1', 'tag2']}
         c.fields_grouped = {}
         search_extras = {}
         fq = ''
         for (param, value) in request.params.items():
             if param not in ['q', 'page', 'sort'] \
                     and len(value) and not param.startswith('_'):
                 if not param.startswith('ext_'):
                     c.fields.append((param, value))
                     fq += ' %s:"%s"' % (param, value)
                     if param not in c.fields_grouped:
                         c.fields_grouped[param] = [value]
                     else:
                         c.fields_grouped[param].append(value)
                 else:
                     search_extras[param] = value

         context = {'model': model, 'session': model.Session,
                    'user': c.user or c.author, 'for_view': True,
                    'auth_user_obj': c.userobj}

         if package_type and package_type != 'dataset':
             # Only show datasets of this particular type
             fq += ' +dataset_type:{type}'.format(type=package_type)
         else:
             # Unless changed via config options, don't show non standard
             # dataset types on the default search page
             if not asbool(
                     config.get('ckan.search.show_all_types', 'False')):
                 fq += ' +dataset_type:dataset'


         facets = OrderedDict()

         default_facet_titles = {
             'organization': _('Organizations'),
             'groups': _('Groups'),
             'tags': _('Tags'),
             'res_format': _('Formats'),
             'license_id': _('Licenses'),
             }

         for facet in g.facets:
             #if facet in default_facet_titles:
             #    facets[facet] = default_facet_titles[facet]
             #else:
                 facets[facet] = facet

         # Facet titles
         for plugin in plugins.PluginImplementations(plugins.IFacets):
             facets = plugin.dataset_facets(facets, package_type)

         c.facet_titles = facets
         limit = g.datasets_per_page
         page = self._get_page_number(request.params)

         data_dict = {
                'q': q,
                'fq': fq.strip(),
                'facet.field': facets.keys(),
                'rows': limit,
                'start': (page - 1) * limit,
                #'sort': sort_by,
                'extras': search_extras
            }
         print "************* fq in filtersearch"
         print q
         print fq
         fq = toolkit.get_or_bust(search_params, 'fq')
        # query = logic.get_action('package_search')(context, data_dict)
         #print(facets)
         # -----------------------------------------------
        #####################################################
        ## Filter resources - copied from after_search

         search_items = ["res_format", "res_extras_par_frequency", "res_extras_par_model", "res_extras_par_experiment","res_extras_par_variables","res_extras_par_ensemble"]
         package_text = ["format", "par_frequency", "par_model", "par_experiment","par_variables","par_ensemble" ]
         max_values_per_item = 40
         num_search_items = len (search_items)
         search_values = [[None for x in range(len(search_items))] for y in range(max_values_per_item)]

         pkg = data_dict
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
         ### End filter resources
        ######################################




         return data_dict

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
        #print "*******after_search"
        #print fq
        #print search_params

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

        #print search_results
        #print search_results['facets']
        #return {'results': search_results}
        return search_results
