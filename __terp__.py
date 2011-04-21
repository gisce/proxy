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
{
    'name': 'Proxy Module',
    'version': '1.0',
    'category': 'Generic Modules/Others',
    'description': """
      * Makes the OpenERP Server a proxy for other OpenERP Servers
    """,
    'author': 'GISCE',
    'website': 'https://github.com/lapunxa/lpx_proxy',
    'depends': ['base'],
    'init_xml': [],
    'update_xml': ["proxy_view.xml"],
    'demo_xml': [],
    'installable': True,
    'active': False,
}