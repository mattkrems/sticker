#!/usr/bin/env python
# -*- coding: utf-8 mode: python -*-

# config_file.py - Module to read sticker config file.
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

import sticker_core as sc
import ConfigParser
import sys, string


# -----------------------------------------------------------
def read_config_file(filename):
    config = ConfigParser.ConfigParser()
    # config.readfp(open('/etc/default/sticker'))
    config.read(filename)

    global_vars = [ 'name',
                    'email',
                    'mail_server',
                    'dpi' ]

    # global section
    for ivar in global_vars:
        try:
            sc.config[ ('STickerConfig', ivar) ] = config.get('STickerConfig', ivar)
        except ConfigParser.NoOptionError:
            print 'Error: config option ' + ivar + ' not found in section [STickerConfig]'
            sys.exit(1)
