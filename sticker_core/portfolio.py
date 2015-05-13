#!/usr/bin/env python
# -*- coding: utf-8 mode: python -*-

# portfolio.py - Class to represent and maintain a portfolio.
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
import symbol_list

# ---------------------------------------------------------------
class Portfolio():
    # -----------------------------------------------------------
    def __init__(self, cash, start_date, trading_commission):
        self.cash = cash
        self.start_date = start_date
        self.transactions = 0
        self.commission = float(trading_commission)
        self.holdings = {}
        self.securities = {}
        self.log = []


    # -----------------------------------------------------------
    def __security_exists(self, security):
        for s in self.holdings.keys():
            if s == security:
                return True
        return False


    # -----------------------------------------------------------
    def print_holdings(self, date):
        my_assets = self.evaluate_assets(date)
        print '| assets   : ', my_assets
        print '| cash     : ', self.cash
        for index in range(0,len(self.log)):
            print '| log      : ', self.log[index]
        for k, v in self.holdings.iteritems():
            print '| portfolio: ' + str(v) + ' x ' + str(k)


    # -----------------------------------------------------------
    def evaluate_assets(self, date):
        asset_sum = 0.0
        for k, v in self.holdings.iteritems():
            security_close = self.securities[k].close.data[self.securities[k].close.get_index(date)]
            asset_sum += v*security_close
        return asset_sum + self.cash


    # -----------------------------------------------------------
    def add_security(self, security, price, num_shares, date):
        if (self.cash - price*num_shares - self.commission) >= 0:
            self.cash = self.cash - price*num_shares - self.commission
            if (self.__security_exists(security.symbol)):
                current_shares = self.holdings[security.symbol]
                self.holdings[security.symbol] = num_shares+current_shares
            else:
                self.holdings[security.symbol] = num_shares
            self.securities[security.symbol] = security
            self.__portfolio_log(date, 'buy', security.symbol, price, num_shares, self.cash)
            self.transactions += 1
        else:
            print "Error: not enough cash to make transaction"


    # -----------------------------------------------------------
    def delete_security(self, security, price, num_shares, date):
        if (self.__security_exists(security.symbol)):
            current_shares = self.holdings[security.symbol]
            if (current_shares >= num_shares):
                self.holdings[security.symbol] = current_shares - num_shares
                self.cash = self.cash + price*num_shares - self.commission
                if (self.holdings[security.symbol] == 0):
                    self.holdings.pop(security.symbol)
                    self.securities.pop(security.symbol)
            self.__portfolio_log(date, 'sell', security.symbol, price, num_shares, self.cash)
            self.transactions += 1
        else:
            print "Error: You do not own this many shares"



    # -----------------------------------------------------------
    def __portfolio_log(self, date, type, security, price, num_shares, cash):
        self.log.append([date, type, security, price, num_shares, cash])
