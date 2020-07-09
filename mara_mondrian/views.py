"""ACL and navigation entries for Saiku"""

import flask
from mara_page import acl, navigation

# The flask blueprint that does
blueprint = flask.Blueprint('mara_mondrian', __name__, static_folder='static',
                            template_folder='templates', url_prefix='/mondrian')

# Defines an ACL resource (needs to be handled by the application)
acl_resource_saiku = acl.AclResource(name='Saiku')


@blueprint.before_app_first_request  # configuration needs to be loaded before we can access it
def _create_acl_resource_for_each_data_set():
    import mara_schema.config
    for data_set in mara_schema.config.data_sets():
        resource = acl.AclResource(name=data_set.name)
        acl_resource_saiku.add_child(resource)


def saiku_navigation_entry():
    return navigation.NavigationEntry(
        label='Saiku', icon='bar-chart', uri_fn=lambda: flask.url_for('mara_mondrian.saiku'),
        description='Pivoting & ad hoc analysis')


@blueprint.route('/saiku')
@acl.require_permission(acl_resource_saiku)
def saiku():
    from mara_mondrian import config

    return flask.redirect(config.mondrian_server_external_url())


@blueprint.route('/saiku/authorize', methods=['POST'])
def saiku_authorize():
    """
    Authorization endpoint for Saiku.

    See https://github.com/project-a/mondrian-server#authentication--acl
    """
    allowed_cubes = [resource.name
                     for resource, allowed
                     in acl.user_has_permissions(flask.request.form['username'], acl_resource_saiku.children)
                     if allowed]

    return flask.jsonify({'allowed': True if allowed_cubes else False, 'cubes': allowed_cubes})
