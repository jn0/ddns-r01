#!/usr/bin/env python3

import sys
import idna
from time import perf_counter
from requests import Session, get
import yaml
from http.cookiejar import DefaultCookiePolicy
from zeep import Client
from zeep.transports import Transport
from IPy import IP


with open('ddns.yaml') as fp:
    config = yaml.load(fp, Loader=yaml.SafeLoader)

resp = get(config['pong'])
if not resp.ok:
    print('Cannot find my IP.', file=sys.stderr)
    sys.exit(1)

try:
    new_ip = IP(resp.text.strip())
except ValueError as e:
    print('Bad IP fetched:', repr(new_ip), file=sys.stderr)
    sys.exit(1)

print('New IP:', new_ip)

try:
    client = None
    session = Session()
    session.cookies.set_policy(policy=DefaultCookiePolicy(rfc2965=True))
    client = Client('https://partner.r01.ru:1443/partner_api.khtml?wsdl',
               transport=Transport(session=session))
    if not client:
        print('No services', file=sys.stderr)
        sys.exit(1)
    print('client=', client)

    login = client.service.logIn(config['user'], config['password'])
    if login.code != 1:
        print('Cannot log in:', login.message, file=sys.stderr)
        sys.exit(1)
    print('login:', login)
    session.headers.update({'Coockie': 'SOAPClient = ' + login.message})

    doms = client.service.getDomainsAllSimple()
    print('domains:', doms)
    if doms.status.code != 1:
        print('No domains.', file=sys.stderr)
        sys.exit(1)

    rr = {}

    for d in doms.data.domainarray_simple:
        t1 = perf_counter()
        r = client.service.getRrRecords(d.name)
        t2 = perf_counter()
        msg = 'ok' if r.status.code == 1 else r.status.message
        print(idna.decode(d.name) if d.name.upper().startswith('XN--') else d.name, t2 - t1, ':', msg)
        rr[d.name.lower()] = r.data

    if config['domain'] not in rr:
        print('No', config['domain'], 'in the list', file=sys.stderr)
        sys.exit(1)

    rr = rr.pop(config['domain'])  # resource records for the domain

    ns0 = client.type_factory('ns0')

    a = None
    for r in rr:
        print(r)
        if r.type_record == 'A':
            a = r
    if not a:
        print('No A-record')
        status = client.service.addNewRrRecord(
            domain=config['domain'].upper(),
            type_record='A',
            params={
                'owner': '',
                'data': str(new_ip),
                'pri': 0,
                'weight': 0,
                'port': 0,
                'sshfp_algorithm': 0,
                'sshfp_type': 0,
                'info': '',
        })
        print('addNewRrRecord:', status)
    else:
        print(a)
        if a.data == str(new_ip):
            print('Same IP:', repr(a.data), '=', new_ip)
            sys.exit(0)

        status = client.service.editRrRecord(a.id, params={
            'owner': a.owner,
            'data': str(new_ip),
            'pri': a.pri,
            'weight': a.weight,
            'port': a.port,
            'sshfp_algorithm': a.sshfp_algorithm,
            'sshfp_type': a.sshfp_type,
            'info': a.info,
        })
        print('editRrRecord:', status)

finally:
    if client:
        print('logout:', client.service.logOut())
# vim:set ft=python ai et ts=4 sts=4 sw=4 cc=80:EOF #
