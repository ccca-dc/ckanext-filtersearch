import ckan.plugins as p
from ckan.common import _, g, c
import ckan.lib.helpers as h
import logging
import ckan.model as model
import ckan.logic as logic
import ckan.logic.schema as schema
import ckan.lib.helpers as h
import ckan.lib.base as base
import ckan.authz as authz
import pylons
from pylons import config
import ckan.lib.datapreview as datapreview
import ckan.lib.plugins
import ckan.plugins as plugins
import pprint

from ckan.common import OrderedDict, c, g, request, _

from paste.deploy.converters import asbool
import ast
import collections

lookup_package_plugin = ckan.lib.plugins.lookup_package_plugin

abort = base.abort
render = base.render

get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError

class ReadController(base.BaseController):
    #######################################################
    ### From ckan Source

    def _read_template(self, package_type):
        return lookup_package_plugin(package_type).read_template()

    #######################################################
    ### From ckan Source
    def _resource_preview(self, data_dict):
        '''Deprecated in 2.3'''
        return bool(datapreview.get_preview_plugin(data_dict,
                                                   return_first=True))
    #######################################################
    ### From ckan Source
    def _setup_template_variables(self, context, data_dict, package_type=None):
        return lookup_package_plugin(package_type).\
            setup_template_variables(context, data_dict)


    def read(self, id):
    #######################################################
    ### From ckan Source
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'auth_user_obj': c.userobj }
        data_dict = {'id': id, 'include_tracking': True}

        #print "**********************Hi read filtersearch"

        # interpret @<revision_id> or @<date> suffix
        split = id.split('@')
        if len(split) == 2:
            data_dict['id'], revision_ref = split
            if model.is_id(revision_ref):
                context['revision_id'] = revision_ref
            else:
                try:
                    date = h.date_str_to_datetime(revision_ref)
                    context['revision_date'] = date
                except TypeError, e:
                    abort(400, _('Invalid revision format: %r') % e.args)
                except ValueError, e:
                    abort(400, _('Invalid revision format: %r') % e.args)
        elif len(split) > 2:
            abort(400, _('Invalid revision format: %r') %
                  'Too many "@" symbols')

        # check if package exists

        #print "********************* anja read"
        try:
            c.pkg_dict = get_action('package_show')(context, data_dict)
            c.pkg = context['package']
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read package %s') % id)

        # used by disqus plugin
        c.current_package_id = c.pkg.id
        #c.related_count = c.pkg.related_count #Comment for Version 2.7 -> Kathi

        # Anja
        num_resources = len(c.pkg_dict['resources'])

        # can the resources be previewed?
        for resource in c.pkg_dict['resources']:
            # Backwards compatibility with preview interface
            resource['can_be_previewed'] = self._resource_preview(
                {'resource': resource, 'package': c.pkg_dict})

            resource_views = get_action('resource_view_list')(
                context, {'id': resource['id']})
            resource['has_views'] = len(resource_views) > 0
            # Anja: MODIFICATION for Kathis resourceversions
            if resource.get('newer_version', '') != '':
                num_resources -= 1

        # Anja
        c.pkg_dict['num_resources'] = num_resources

        package_type = c.pkg_dict['type'] or 'dataset'
        self._setup_template_variables(context, {'id': id},
                                       package_type=package_type)

        template = self._read_template(package_type)

        ######################### MODIFICATION, Anja 27.7.17 ############################
        ### Check if we need to display resource facets
        #num_resources =  c.pkg.num_resources if c.pkg.num_resources else len(c.pkg_dict['resources'])
        conf_resources = config.get(
            'ckanext.filtersearch.facet_resources', False)
        #print "******************** Read before search ********************************"
        #print c.facets
        #print c.search_facets

        c.filtered_dict = None

        if conf_resources and  num_resources > int(conf_resources):

                # Prepare query on package - copied from package controller - search
                # to get actual facet list and items
                facets = OrderedDict()

                default_facet_titles = {
                    'organization': _('Organizations'),
                    'groups': _('Groups'),
                    'tags': _('Tags'),
                    'res_format': _('Formats'),
                    'license_id': _('Licenses'),
                    }

                for facet in g.facets:
                    if facet in default_facet_titles:
                        facets[facet] = default_facet_titles[facet]
                    else:
                        facets[facet] = facet

                # Facet titles
                for plugin in plugins.PluginImplementations(plugins.IFacets):
                    facets = plugin.dataset_facets(facets, package_type)

                # remove all facets which are not resource_facets (res_*)
                for x in facets:
                    if not x.startswith("res_"):
                        facets.pop(x)

                c.facet_titles = facets
                c.fields = []
                c.fields_grouped = {}
                search_extras = {}
                search_extras['name'] = id
                #Dies ist wichtig:
                fq = ' name:"%s"' % (id)

                #print type(request.params.items())
                #print request.params.items()
                #print request.params

                for (param, value) in request.params.items():
                    #Facet Query only for resource fields
                    if param not in ['q', 'page', 'sort'] \
                            and len(value) and param.startswith('res_'):
                        c.fields.append((param, value))
                        fq += ' %s:"%s"' % (param, value)
                        if param not in c.fields_grouped:
                            c.fields_grouped[param] = [value]

                search_dict = {
                       'fq': fq.strip(),
                       'facet.field': facets.keys(),
                      # 'rows': limit,
                       #'start': (page - 1) * limit,
                       #'sort': sort_by,
                       'extras': search_extras
                   }

                c.facet_titles = facets
                query = get_action('package_search')(context, search_dict)
                c.facets = query['facets']
                c.search_facets = query['search_facets']

                ###### If we have ONE pkg Dict as result in query this is already the filtered resource Dict
                # Thus modify the current package dict to only show the selected resources

                #pprint.pprint(query['results'][0])
                #print c.pkg
                if query['count'] == 1:
                    c.filtered_dict = query['results'][0]
                    # set tracking info .. copied from CKAN - let to an error if not present
                    for res in c.filtered_dict['resources']:
                        tracking_summary = model.TrackingSummary.get_for_resource(res['url'])
                        res['tracking_summary'] = tracking_summary
                else:
                    c.filtered_dict = None # Sure?????

                # For Kathi and Version 2.7
                context['filtered_dict'] = c.filtered_dict
                context['facet_titles'] = c.facet_titles
                context['search_facets'] = c.search_facets
                context['facets'] = c.facets
                context['fields'] = c.fields
        ######################### MODIFICATION, Anja 27.7.17  END ############################


        package_type = c.pkg_dict['type'] or 'dataset'
        self._setup_template_variables(context, {'id': id},
                                       package_type=package_type)

        template = self._read_template(package_type)
        #print "************************ TMPLATE"
        #print template
        #print "**********************End read filtersearch"

        #pprint.pprint(c.pkg_dict)
        #pprint.pprint(context)
        try:
            return render(template,
                          extra_vars={'dataset_type': package_type})
        except ckan.lib.render.TemplateNotFound:
            msg = _("Viewing {package_type} datasets in {format} format is "
                    "not supported (template file {file} not found).".format(
                        package_type=package_type, format=format,
                        file=template))
            abort(404, msg)

        assert False, "We should never get here"


        ### From ckan Source END
        #######################################################
