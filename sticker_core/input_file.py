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
def read_input_file(filename):
    config = ConfigParser.ConfigParser()
    # config.readfp(open('/etc/default/sticker'))
    config.read(filename)

    input_vars  = \
        { 'strategy_label'       : 'simple_strategy',
          'enter_signal'         : 'rsi(14) < 45',
          'exit_signal'          : 'rsi(14) > 80',
          'risk_cap'             : 'close < 0.9 * purchase',
          'starting_cash'        : '1000',
          'chart_functions'      : 'l_b_band(20,2):c_b_band(20,2):u_b_band(20,2);rsi(14)',
          'chart_functions_new'  : 'l_b_band(20,2):y % c_b_band(20,2):g % u_b_band(20,2):y | rsi(14):b',
          'symbol_blacklist'     : '',
          'symbol_select'        : 'mcap > 1.0',
          'trading_symbols'      : 'DJI',
          'trading_start'        : '20090103',
          'trading_end'          : '20091003',
          'trading_type'         : 'long_buy',
          'trading_commission'   : '4.5',
          'always_plot'          : 'False' }

    # find out which backtest configs we should use
    try:
        run_backtest = config.get('BacktestConfig', 'run_backtest')
        run_backtest = string.replace(run_backtest, ' ', '')
        backtest_indices = string.split(run_backtest, ',')
        sc.input[ ('BacktestConfig', 'run_backtest') ] = backtest_indices
    except:
        print 'Warning: config option run_backtest not found in section [BacktestConfig]'
        print '         using default: 001'
        backtest_indices = '001'
        sc.input[ ('BacktestConfig', 'run_backtest') ] = [ backtest_indices ]

    sections = []
    for index in sc.input[ ('BacktestConfig', 'run_backtest') ]:
        sections.append('BacktestStrategy_' + index)

    # read trading blocks
    for section in sections:
        for ivar, value in input_vars.iteritems():
            try:
                config_var = config.get(section, ivar)
                sc.input[ (section, ivar) ] = config_var.replace('\n',' ')
            except:
                print 'Warning: config option ' + ivar + ' not found in section [' + section + ']'
                print '         of the config file. using default: ', input_vars[ ivar ]
                sc.input[ (section, ivar) ] = input_vars[ ivar ]
