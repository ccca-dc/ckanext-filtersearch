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
from ckanext.filtersearch import helpers as h

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
                   'auth_user_obj': c.userobj}
        data_dict = {'id': id, 'include_tracking': True}

        #print "************ filtersearch read"
        #print id
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

        ####################### Anja New, 21.12.17

        corrected_id = h.filtersearch_check_id (id)
        data_dict['id'] = corrected_id
        #print corrected_id
        #######################End new ################

        # check if package exists
        try:
            c.pkg_dict = get_action('package_show')(context, data_dict)
            c.pkg = context['package']
            print c.pkg
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read package %s') % data_dict['id'])

        # used by disqus plugin
        c.current_package_id = c.pkg.id
        c.related_count = c.pkg.related_count

        # can the resources be previewed?
        for resource in c.pkg_dict['resources']:
            # Backwards compatibility with preview interface
            resource['can_be_previewed'] = self._resource_preview(
                {'resource': resource, 'package': c.pkg_dict})

            resource_views = get_action('resource_view_list')(
                context, {'id': resource['id']})
            resource['has_views'] = len(resource_views) > 0

        package_type = c.pkg_dict['type'] or 'dataset'
        self._setup_template_variables(context, {'id': id},
                                       package_type=package_type)

        template = self._read_template(package_type)
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
