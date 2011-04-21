# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Eduard Carreras i Nadal <ecarreras@gmail.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import netsvc
import pooler
import xmlrpclib
from osv import osv, fields

_PROXY_SERVERS = {}

class ProxyRemotes(osv.osv):
    """Model for manage Proxy Remotes."""

    _name = 'proxy.remotes'

    _columns = {
      'name': fields.char('Description', size=255, required=True),
      'host': fields.char('Host', size=255, required=True),
      'port': fields.integer('Port', required=True),
      'active': fields.boolean('Active'),
    }

    _defaults = {
        'host': lambda *a: 'localhost',
        'port': lambda *a: 2000,
        'active': lambda *a: 1,
    }

ProxyRemotes()

def is_local(db):
    return db in netsvc.SERVICES['db'].list()

def proxy_db_list():
    """Lists all databases behind proxy.
    """
    res = []
    uid = 1
    up_servers = []
    for dbname in netsvc.SERVICES['db'].list():
        res.append(dbname)
        # Check proxies in this database
        dba, pool = pooler.get_db_and_pool(dbname)
        cursor = dba.cursor()
        try:
            proxy_obj = pool.get('proxy.remotes')
            pr_ids = proxy_obj.search(cursor, uid, [])
            for proxy in proxy_obj.browse(cursor, uid, pr_ids):
                dbsock = xmlrpclib.ServerProxy('http://%s:%i/xmlrpc/db' %
                                               (proxy.host, proxy.port))
                for remote_db in dbsock.list():
                    res.append(remote_db)
                    up_servers.append(remote_db)
                    _PROXY_SERVERS[remote_db] = (proxy.host, proxy.port)
        except Exception:
            pass
        finally:
            cursor.close()
    # Drop from the dict servers unreachables
    for proxy_db in _PROXY_SERVERS.keys():
        if proxy_db not in up_servers:
            del _PROXY_SERVERS[proxy_db]
    return res

# Overwrite the db.list() method
netsvc.SERVICES['db']._methods['list'] = proxy_db_list

class LocalServiceProxy(netsvc.Service):
    def __init__(self, name):
        self.__name = name
        try:
            self._service = netsvc.SERVICES[name]
            for m_name, m_definition in self._service._methods.items():
                setattr(self, m_name, m_definition)
        except KeyError, keyError:
            logger = netsvc.Logger()
            logger.notifyChannel('module', netsvc.LOG_ERROR,
                                'This service does not exists: %s'
                                % (str(keyError),) )
            raise
    def __call__(self, method, *params):
        if len(params):
            if is_local(params[0]):
                return getattr(self, method)(*params)
            else:
                proxy = _PROXY_SERVERS[params[0]]
                sock = xmlrpclib.ServerProxy('http://%s:%i/xmlrpc/%s' %
                                             (proxy[0], proxy[1], self.__name))
                # Add a try-except-finally if errors occurs,
                # disconnect the socket
                try:
                    res = getattr(sock, method)(*params)
                except Exception, exc:
                    raise exc
                return res
        else:
            return getattr(self, method)(*params)

# Overwrite the dispatcher
netsvc.LocalService = LocalServiceProxy
