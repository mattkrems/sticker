#!/usr/bin/env python
# -*- coding: utf-8 mode: python -*-

# symbol_list.py - Module to deal with lists of symbols.
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

import anydbm
import sticker_core as sc
import symbol
import string

import datetime
import numpy as np

# -----------------------------------------------------------
class SymbolList():
    # -------------------------------------------------------
    def __init__(self, symbol_list, symbol_blacklist, start_date, end_date):
        self.symbols = self.__expand_list(symbol_list, symbol_blacklist)
        self.components = {}
        for csym in self.symbols:
            self.components[ csym ] = symbol.Symbol(csym, start_date, end_date)


    # -------------------------------------------------------
    def __expand_list(self, symbol_list, symbol_blacklist):
        symbols = string.split(symbol_list.strip(' '), ',')
        expanded_list = [symbol.strip(' ') for symbol in symbols]
        for iname in symbols:
            index_name = iname.strip(' ')
            try:
                index_length = sc.stock_indices[ index_name ]
                db_name  = sc.cache_dir + '/index/' + index_name + '_' + \
                           str(index_length) + '.db'
                db       = anydbm.open(db_name, 'c')
                expanded_list.remove(index_name)
                for key in db.keys():
                    expanded_list.append(key)
                db.close()
            except: pass
        blacklist = string.split(symbol_blacklist.strip(' '), ',')
        if len(blacklist) > 0:
            for symbol in blacklist:
                ssymbol = symbol.strip(' ')
                try:
                    expanded_list.remove(ssymbol)
                    print 'blacklisting: ', ssymbol
                except: pass
        # return list without dupes
        return list(set(expanded_list))


    # -------------------------------------------------------
    def evaluate(self, start_date, end_date, criteria, expression):
        # local functions used for shorthand

        for symbol_name, symbol in self.components.iteritems():
            # -----------------------------------------------
            def omax():
                return symbol.open.max(start_date, end_date)
            # -----------------------------------------------
            def omin():
                return symbol.open.min(start_date, end_date)
            # -----------------------------------------------
            def cmax():
                return symbol.close.max(start_date, end_date)
            # -----------------------------------------------
            def cmin():
                return symbol.close.min(start_date, end_date)

            if eval(criteria):
                print '%-4s' % symbol_name, eval(expression)

if __name__ == '__main__':
    k=symbol_list.SymbolList('GOOG,BAC','',datetime.date(2010,7,16), datetime.date.today())
