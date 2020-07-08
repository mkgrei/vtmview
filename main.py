import os
import json
import click
import requests
from requests.auth import HTTPBasicAuth
from tabulate import tabulate

import urllib3
urllib3.disable_warnings()

vtm_url = os.getenv('vtm_url')
u = os.getenv('vtm_user')
p = os.getenv('vtm_pswd')

auth = HTTPBasicAuth(u, p)

base = "/api/tm/6.0/config/active/"

def get_resources():
    url = vtm_url + base
    res = requests.get(url, auth=auth, verify=False)

    data = json.loads(res.text)

    resource = [[i['name']] for i in data['children']]
    print(tabulate(resource, headers=['resources']))



resources = [
        'extra_files',
        'license_keys',
        'monitor_scripts',
        'monitors',
        'persistence',
        'pools',
        'rules',
        'traffic_ip_groups',
        'traffic_managers',
        'virtual_servers',
        ]

def get_resource(key):
    url = vtm_url + base + key
    res = requests.get(url, auth=auth, verify=False)

    data = json.loads(res.text)

    resource = [[i['name']] for i in data['children']]
    print(tabulate(resource, headers=[key + ':name']))

def get_pools():
    url = vtm_url + base + 'pools'
    res = requests.get(url, auth=auth, verify=False)

    data = json.loads(res.text)

    pools = [i['name'] for i in data['children']]

    ans = []
    for pool in pools:
        purl = vtm_url + base + 'pools/' + pool
        res = requests.get(purl, auth=auth, verify=False)

        data = json.loads(res.text)
        basic = data['properties']['basic']

        nodes = [n['node'] for n in basic['nodes_table']]
        ips = [n.split(':')[0] for n in nodes]
        ports = list(set([n.split(':')[1] for n in nodes]))
        assert len(ports) == 1
        ports = ports[0]
        monitors = basic['monitors']
        transparency = basic['transparent']

        ans.append([pool, ','.join(ips), ports, ','.join(monitors), transparency])
    print(tabulate(ans, headers=['pool:name', 'nodes', 'port', 'monitors', 'transparent']))

def get_virtual_servers():
    url = vtm_url + base + 'virtual_servers'
    res = requests.get(url, auth=auth, verify=False)

    data = json.loads(res.text)

    vss = [i['name'] for i in data['children']]

    ans = []
    for vs in vss:
        vurl = vtm_url + base + 'virtual_servers/' + vs
        res = requests.get(vurl, auth=auth, verify=False)

        data = json.loads(res.text)
        basic = data['properties']['basic']

        port = basic['port']
        enabled = basic['enabled']
        pool = basic['pool']
        vips = basic['listen_on_traffic_ips']

        ans.append([vs, port, enabled, pool, ','.join(vips)])
    print(tabulate(ans, headers=['virtual_server:name', 'port', 'enabled', 'pool', 'vips']))

def get_traffic_ip_groups():
    url = vtm_url + base + 'traffic_ip_groups'
    res = requests.get(url, auth=auth, verify=False)

    data = json.loads(res.text)

    tips = [i['name'] for i in data['children']]

    ans = []
    for tip in tips:
        turl = vtm_url + base + 'traffic_ip_groups/' + tip
        res = requests.get(turl, auth=auth, verify=False)

        data = json.loads(res.text)
        basic = data['properties']['basic']

        enabled = basic['enabled']
        ips = basic['ipaddresses']
        machines = basic['machines']
        mode = basic['mode']
        ipmode = basic['ip_assignment_mode']
        slaves = basic['slaves']

        ans.append([tip, enabled, ','.join(ips), ','.join(machines), mode, ipmode, ','.join(slaves)])
    print(tabulate(ans, headers=['traffic_ip_group:name', 'enabled', 'ips', 'machines', 'mode', 'ip_assignment_mode', 'slaves']))

def get_json(key, name):
    url = vtm_url + base + key + '/' + name
    res = requests.get(url, auth=auth, verify=False)

    data = json.loads(res.text)

    print(json.dumps(data, indent=2))

@click.command()
@click.option("--resource", prompt=",".join(resources))
@click.option("--name", prompt='all or resource name')
def main(resource, name):
    if resource not in resources + ['vs', 'tip']:
        print("resource types: " + ",".join(resources))
        return
    if name == 'all':
        if resource in ['pools']:
            get_pools()
        elif resource in ['virtual_servers', 'vs']:
            get_virtual_servers()
        elif resource in ['traffic_ip_groups', 'tip']:
            get_traffic_ip_groups()
        else:
            get_resource(resource)
        return
    get_json(resource, name)

if __name__ == '__main__':
    main()
