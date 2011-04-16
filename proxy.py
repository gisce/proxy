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
from osv import osv,fields
from proxy_rpc import ProxyRPC

LOCAL_DBS = {}
REMOTE_DBS = {}
ERPS = {}

_PROXY_REMOTES_CACHE = {} #{ID: socket}
_PROXY_DATABASES_CACHE = {} # {Database: ID}

class ProxyRemotes(osv.osv):
    """Model for manage Proxy Remotes."""

    _name = 'proxy.remotes'
    _description = 'Remote Servers to connect from proxy'

    _columns = {
      'name': fields.char('Description', size=255, required=True),
      'host': fields.char('Host', size=255, required=True),
      'port': fields.integer('Port', required=True),
    }

    _defaults = {
        'host': lambda *a: 'localhost',
        'port': lambda *a: 2000,
    }
    
    def __init__(self, pool, cursor):
        """Init proxy databases.
        """
        super(ProxyRemotes, self).__init__(pool, cursor)
        try:
            proxy_obj = self.pool.get('proxy.remotes')
            UID = 1
            ids = proxy_obj.search(cursor, UID, [])
            for erp in self.read(cursor, UID, ids):
                rpc = ProxyRPC(erp['host'], erp['port'])
                _PROXY_REMOTES_CACHE[erp['id']] = rpc
                for dbname in rpc.db_list():
                    _PROXY_DATABASES_CACHE = {dbname: rpc}
        except Exception:
            pass

ProxyRemotes()

def is_local(db):
    return db in LOCAL_DBS.keys()

def proxy_db_list():
    """Lists all databases behind proxy.
    """
    res = []
    res.extend(netsvc.SERVICES['db'].list())
    res.extend(_PROXY_DATABASES_CACHE.keys())
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
                rpc = _PROXY_DATABASES_CACHE.get(params[0], None)
                # Add a try-except-finally if errors occurs,
                # disconnect the socket
                try:
                    res = rpc.send((self.__name, method, params[0])+params[1:])
                except Exception, exc:
                    raise exc
                finally:
                    if rpc:
                        rpc.disconnect()
                return res

# Overwrite the dispatcher
netsvc.LocalService = LocalServiceProxy
