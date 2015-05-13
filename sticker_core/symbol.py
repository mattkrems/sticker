#!/usr/bin/env python
# -*- coding: utf-8 mode: python -*-

# symbol.py - Module to add symbols to the database
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
import time_series, util
import os, anydbm, time
import urllib
import datetime

# ---------------------------------------------------------------
class Symbol():
    # -----------------------------------------------------------
    def __init__(self, symbol, start_date, end_date):
        self.symbol = symbol

        # check if in database or add to database
        self.__add(start_date, end_date)

        # fill lists with data and make a times dictionary
        times, open, high, low, close, volume, adj_close = self.__read_db(start_date, end_date)

        # fill fields with time series information
        self.open      = time_series.TimeSeries(times, open)
        self.high      = time_series.TimeSeries(times, high)
        self.low       = time_series.TimeSeries(times, low)
        self.close     = time_series.TimeSeries(times, close)
        self.volume    = time_series.TimeSeries(times, volume)
        self.adj_close = time_series.TimeSeries(times, adj_close)

        # add extra market information to symbol object
        self.extra = self._read_db_extra()

    # -----------------------------------------------------------
    def __add(self, start_date, end_date):
        '''checks if symbol and dates are in database and adds them if they
        are not'''

        db = self.__open_db()

        # check database for the data we want to insert
        missing = self.__find_missing(start_date, end_date, db)

        # add the missing dates if there are any
        if len(missing) == 0:
            return None
        elif len(missing) >= 1:
            self.__insert_symbol(missing[0], missing[-1], db)

        # close database to save data
        db.close()


    # -----------------------------------------------------------
    def __find_missing(self, start_date, end_date, db):
        missing = []

        d = start_date
        while d <= end_date:
            try:
                db[d.isoformat()]
            except KeyError:
                missing.append(d)
            d = d + datetime.timedelta(1)
        return missing

    # -----------------------------------------------------------
    def __insert_symbol(self, start_date, end_date, db):       
        list = self.__get_historical_prices(self.symbol, start_date, end_date)
        if len(list) == 1:
            return None

        last_trade_date = list[1][0]
        days_without_trade = util.date_range(start_date, last_trade_date)

        # fill dictionary with data for trading days
        for i in range(1,len(list)):
            trade_date = list[i][0]
            days_without_trade.remove(trade_date)

            data = ''
            for j in range(1, len(list[i])):
                data = data + str(list[i][j]) + ' '
            db[ trade_date.isoformat() ] = data
            
        # make the data for non-trading days '0'
        for i in days_without_trade:
            db [i.isoformat()] = '0'

    # -----------------------------------------------------------
    def __read_db(self, start_date, end_date):
        db = self.__open_db()
        date_range = util.date_range(start_date, end_date)

        times = []
        open  = []
        high  = []
        low   = []
        close = []
        volume    = []
        adj_close = []
        for d in date_range:
            try:
                data = db[d.isoformat()]
            except:
                data = '0'

            if data != '0':
                data = data.split()
                times.append(d)
                open.append(float(data[0]))
                high.append(float(data[1]))
                low.append(float(data[2]))
                close.append(float(data[3]))
                volume.append(float(data[4]))
                adj_close.append(float(data[5]))

        return times, open, high, low, close, volume, adj_close

    # -----------------------------------------------------------
    def __open_db(self):
        db_dir = sc.cache_dir + '/symbol'
        if not os.path.isdir(db_dir): os.mkdir(db_dir)
        db_name = db_dir + '/' + self.symbol + '.db'
        return anydbm.open(db_name, 'c')


    # -----------------------------------------------------------
    def __get_historical_prices(self, symbol, start_date, end_date):

        url = 'http://ichart.yahoo.com/table.csv?s=%s&' % symbol + \
              'a=%s&' % str(start_date.month - 1) + \
              'b=%s&' % str(start_date.day)     + \
              'c=%s&' % str(start_date.year)     + \
              'd=%s&' % str(end_date.month - 1)   + \
              'e=%s&' % str(end_date.day)       + \
              'f=%s&' % str(end_date.year)       + \
              'g=d&ignore=.csv'

        print 'Quering Yahoo!... %-4s (%s, %s)' % (symbol, start_date, end_date), url
        days = urllib.urlopen(url).readlines()
        data = [day[:-2].split(',') for day in days]

        # convert dates to datetime objects
        for i in range(1,len(data)):
            d = data[i][0]
            print "WOW"
            print d
            data[i][0] = datetime.date(int(d[0:4]),int(d[5:7]),int(d[8:10]))

        return data

    # -----------------------------------------------------------
    def _read_db_extra(self):
        db_dir = sc.cache_dir + '/symbol_extra'
        if not os.path.isdir(db_dir): os.mkdir(db_dir)
        db_name = db_dir + '/' + self.symbol + '_extra.db'
        db = anydbm.open(db_name, 'c')

        self._get_extra(db)
        dict = {}
        for key in db.keys():
            dict[key] = db[key]
        return dict

    # -----------------------------------------------------------
    def _get_extra(self, db):
        # database can only have strings in it
        today = time.strftime('%Y%m%d', time.localtime())
        try:
            date = db['date'] 
        except KeyError:
            date = None

        if date != today:
            self._add_extra(self.symbol,db)
            db['date'] = today

    # -----------------------------------------------------------
    def _add_extra(self, symbol, db):
        """
        Get all available quote data for the given ticker symbol.

        Returns a dictionary.
        """
        values = self._request(symbol, 'l1c1va2xj1b4j4dyekjm3m4rr5p5p6s7n').split(',')
        print 'Quering Yahoo!... %-4s' % symbol
        db['price'] = values[0]
        db['change'] = values[1]
        db['volume'] = values[2]
        db['avg_daily_volume'] = values[3]
        db['stock_exchange'] = values[4]
        db['market_cap'] = values[5]
        db['book_value'] = values[6]
        db['ebitda'] = values[7]
        db['dividend_per_share'] = values[8]
        db['dividend_yield'] = values[9]
        db['earnings_per_share'] = values[10]
        db['52_week_high'] = values[11]
        db['52_week_low'] = values[12]
        db['50day_moving_avg'] = values[13]
        db['200day_moving_avg'] = values[14]
        db['price_earnings_ratio'] = values[15]
        db['price_earnings_growth_ratio'] = values[16]
        db['price_sales_ratio'] = values[17]
        db['price_book_ratio'] = values[18]
        db['short_ratio'] = values[19]
        db['name'] = values[20].strip('"')

    # -----------------------------------------------------------
    def _request(self, symbol, stat):
        url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=%s' % (symbol, stat)
        return urllib.urlopen(url).read().strip().strip('"')


#----------------------------------------------------------------
if __name__ == '__main__':
    k = Symbol('GOOG', datetime.date(2010,7,16), datetime.date.today())
    c = k.close.hist_changes(datetime.date(2010,7,16), datetime.date(2010,7,30) )
    #a = k.close.hist_adv('20090902', '20090910', 1)
    #d = k.close.hist_dec('20090902', '20090910', 1)

    print 'c: ', c.time_hash, c.data
    #print 'a: ', a.data
    #print 'd: ', d.data
