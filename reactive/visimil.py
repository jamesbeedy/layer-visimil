import os

from charms.reactive import (
    when, when_any, when_not, set_state, remove_state
)

from charmhelpers.core.hookenv import (
    open_port, status_set, unit_private_ip, config, log
)

from charmhelpers.core import unitdata

from charms.layer.visimil import (
    VISIMIL_SNAP_CONFIG_DIR,
    VISIMIL_PORT
)

from charms.layer.nginx import configure_site


kv = unitdata.kv()


@when_not('manual.elasticsearch.check.available')
def check_user_provided_elasticsearch():
    if not config('es-hosts'):
        remove_state('visimil.manual.elasticsearch.available')
        log("Manual elasticsearch not configured")
    else:
        kv.set('es_hosts', config('es-hosts'))
        set_state('visimil.manual.elasticsearch.available')
        remove_state('visimil.elasticsearch.available')
        remove_state('visimil.juju.elasticsearch.available')
    set_state('manual.elasticsearch.check.available')


@when_not('visimil.conf.dir.available')
def create_visimil_conf_dir():
    """Ensure config dir exists
    """
    if not os.path.isdir(VISIMIL_SNAP_CONFIG_DIR):
        os.makedirs(VISIMIL_SNAP_CONFIG_DIR)
    set_state('visimil.conf.dir.available')


@when('elasticsearch.available')
def render_elasticsearch_lb(elasticsearch):
    """Write render elasticsearch cluster loadbalancer
    """
    status_set('maintenance',
               'Configuring application for elasticsearch')

    ES_SERVERS = []
    for unit in elasticsearch.list_unit_data():
        ES_SERVERS.append(unit['host'])

    kv.set('es_hosts', ",".join(ES_SERVERS))

    status_set('active', 'Elasticsearch available')

    remove_state('elasticsearch.broken')
    remove_state('visimil.elasticsearch.available')
    remove_state('visimil.manual.elasticsearch.available')
    set_state('visimil.juju.elasticsearch.available')


@when_any('visimil.juju.elasticsearch.available',
          'visimil.manual.elasticsearch.available')
@when('nginx.available')
@when_not('visimil.elasticsearch.available')
def configure_es_proxy_hosts():
    """Write out the nginx config containing the es servers
    """

    ES_SERVERS = []

    for host in kv.get('es_hosts').split(","):
        ES_SERVERS.append({'host': host, 'port': "9200"})

    configure_site('es_cluster', 'es_cluster.conf.tmpl',
                   es_servers=ES_SERVERS)

    set_state('visimil.elasticsearch.available')


@when('visimil.juju.elasticsearch.available')
@when_not('elasticsearch.lb.proxy.available')
def render_elasticsearch_lb_proxy():
    """Write out elasticsearch lb proxy
    """
    status_set('maintenance', 'Configuring elasticsearch loadbalancing proxy')
    configure_site('es_lb_proxy', 'es_lb_proxy.conf.tmpl')
    status_set('active', 'Elasticsearch loadbalancer/proxy configured')
    # Set state
    set_state('elasticsearch.lb.proxy.available')


@when_not('visimil.web.available')
@when('visimil.elasticsearch.available', 'elasticsearch.lb.proxy.available')
def open_port_set_avail():
    open_port(VISIMIL_PORT)
    status_set(
        "active", "Visimil Available at http://{}:{}".format(
            unit_private_ip(), VISIMIL_PORT))
    set_state('visimil.web.available')


@when_any('elasticsearch.broken',
          'config.changed.es-hosts')
@when('visimil.web.available')
def modify_elasticsearch_config():
    remove_state('manual.elasticsearch.check.available')
    remove_state('visimil.juju.elasticsearch.available')
    remove_state('visimil.elasticsearch.available')


@when('http.available', 'visimil.web.available')
def configure_http_interface(http):
    http.configure(port=VISIMIL_PORT)
