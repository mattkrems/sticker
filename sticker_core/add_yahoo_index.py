#!/usr/bin/env python
# -*- coding: utf-8 mode: python -*-

# add_yahoo_index.py - Module to query Yahoo for symbols
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

import sticker_core
import os, anydbm, urllib, string


# -----------------------------------------------------------
def query_all_indices(stock_indices):
    print '----[ Query Indices ]-------------------------------'
    for k, v in stock_indices.iteritems():
        print '| index = ' + k
        print '| constituent stocks = ' + str(v)
        print '| ----[ Update ' + k + ' Index Symbol Data ]--------------'
        add_symbol.add('^' + k)
        print 'done\n'
    return query_index(k, v)


# -----------------------------------------------------------
def query_index(index_name, index_length):
    base_url = 'http://download.finance.yahoo.com/d/quotes.csv'
    query    = 's=@%5E' + index_name + '&f=sn&e=.csv'
    # open database
    index_dir = sticker_core.cache_dir + '/index'
    if not os.path.isdir(index_dir): os.mkdir(index_dir)
    db_name  = index_dir + '/' + index_name + '_' + str(index_length) + '.db'
    db       = anydbm.open(db_name, 'c')

    index_components = []
    query_size   = 50  # Yahoo only gives 50 entries per query
    current_iter = 0
    nqueries     = index_length // query_size + 1
    mqueries     = index_length % query_size
    print '----[ Make Index Database ]-----------------------'
    for x in range(0, nqueries):
        query_iter = '&h=' + str(current_iter)
        query_url  = base_url + '?' + query + query_iter
        print 'Quering Yahoo!... %-4s' % index_name, query_url
        query_out  = urllib.urlopen(query_url)
        lines      = split_lines(query_out.read())
        if x == nqueries - 1:
            nrange = mqueries
        else:
            nrange = query_size
        if x > 0: nrange += 1
        for y in range(0, nrange):
            split_line = string.split(lines[y], ',')
            db[ split_line[0].strip('"') ] = split_line[1].strip('"')
            index_components.append(split_line[0].strip('"'))
        current_iter += query_size

    db.close()
    print 'done\n'
    return index_components


# -----------------------------------------------------------
def split_lines(buf):
    def remove_carriage(s):
        if s[-1] == '\r': return s[:-1]
        else: return s
    return map(remove_carriage,filter(lambda x:x, string.split(buf, '\n')))


# -----------------------------------------------------------
def update_stocks(index_components, start_date, end_date):
    for i in range(len(index_components)):
        add_symbol.add(index_components[i], start_date, end_date)


# -----------------------------------------------------------
def add(stock_indices,
        start_date = sticker_core.def_start,
        end_date   = sticker_core.def_end):

    index_components = query_all_indices(stock_indices)
    print '----[ Update Stock Database ]-------------------'
    update_stocks(index_components, start_date, end_date)
