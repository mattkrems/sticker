#!/usr/bin/env python
# -*- coding: utf-8 mode: python -*-

# __init__.py - Initializing module for package sticker
#
# Copyright (c) 2009, Heiko Appel, Matt Krems
#
# This program is free software; you can redistribute it and/or
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import os, datetime

# -----------------------------------------------------------
__author__    = "Heiko Appel, Matt Krems"
__version__   = "0.1"
__date__      = "2009-09-19"
__copyright__ = "Copyright (c) 2009 Heiko Appel, Matt Krems"
__license__   = "GPL"


# -----------------------------------------------------------
package_name      = 'sticker'
package_version   = __version__
package_copyright = __copyright__
package_license   = __license__


# -----------------------------------------------------------
home_dir    = os.path.expanduser('~')
sticker_dir = home_dir + '/.sticker'
cache_dir   = sticker_dir + '/database'
if not os.path.isdir(sticker_dir): os.mkdir(sticker_dir)
if not os.path.isdir(cache_dir): os.mkdir(cache_dir)

def_start = datetime.date(2009,1,1)
def_end   = datetime.date.today()

verbose    = False
send_email = False

# used to store content of config file
config   = {}

# used to store content of input file
input    = {}

# -----------------------------------------------------------
stock_indices = { 'GDAXI'     :   30,
                  'FCHI'      :   37,
                  'STOXX50E'  :   47,
                  'IXIC'      : 2798,
                  'GSPC'      :  500,
                  'DJI'       :   30,
                  'FTSE'      :  100,
                  'BVSP'      :   63,
                  'AXJO'      :  200,
                  'HSI'       :   38,
                  'IBEX'      :   32  }
