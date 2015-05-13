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

import symbol
import pickle
import anydbm

def gen_ts_fixture():
    # time for methods to start at
    m_start = '20030102'
    # time series end time
    end = '20091009'

    # open database
    db = anydbm.open('test_time_series.db', 'c')

    # add time series to database
    security = symbol.Symbol('AMZN', '20000103', end)
    ts = security.close
    db[ 'time_series_1' ] = pickle.dumps(ts)

    # add dates to database
    db[ 'm_start' ] = m_start
    db[ 'end' ] = end

    # add method returns to database
    db['max']          = pickle.dumps(ts.max(m_start, end))

    db['min']          = pickle.dumps(ts.min(m_start, end))

    db['sum']          = pickle.dumps(ts.sum(m_start, end))

    db['m_sum']        = pickle.dumps(ts.m_sum(m_start, end, 10))

    db['avg']          = pickle.dumps(ts.avg(m_start, end))

    db['m_avg']        = pickle.dumps(ts.m_avg(m_start, end, 10))

    db['exp_m_avg']    = pickle.dumps(ts.exp_m_avg(m_start, end, 10, None))

    db['hist_changes'] = pickle.dumps(ts.hist_changes(m_start, end, 1))

    db['hist_adv']     = pickle.dumps(ts.hist_adv(m_start, end, 1))

    db['hist_dec']     = pickle.dumps(ts.hist_dec(m_start, end, 1))

    db['rsi']          = pickle.dumps(ts.rsi(m_start, end, 10))

    db['exp_rsi']      = pickle.dumps(ts.exp_rsi(m_start, end, 10))

    db['stdev']        = pickle.dumps(ts.stdev(m_start, end, 10))

    db['b_bands']      = pickle.dumps(ts.b_bands(m_start, end, 10, 2))

    db['low']          = pickle.dumps(ts.low(m_start, end, 1))

    db['high']         = pickle.dumps(ts.high(m_start, end, 1))

    low  = security.low.low(m_start, end, 10)
    high = security.high.high(m_start, end, 10)
    db['fsto_k']       = pickle.dumps(ts.fsto_k(low, high, m_start, end, 10))


    db['mfi']          = pickle.dumps(ts.mfi(security.high,
                                             security.low,
                                             security.close,
                                             security.volume,
                                             m_start, 
                                             end,
                                             10))

    db['monotonous_up'] = pickle.dumps(ts.monotonous_up(end, 10))

    db['monotonous_down'] = pickle.dumps(ts.monotonous_down(end, 10))

    db['historic_spread'] = pickle.dumps(ts.historic_spread(end, 10))
    
    db['roc'] =  pickle.dumps(ts.roc(end, 10))

    db['derivative'] = pickle.dumps(ts.derivative(m_start, end))

    db['derivative_m_avg'] = pickle.dumps(ts.derivative_m_avg(m_start, end, 10))

                                             



    





if __name__ == '__main__':
    gen_ts_fixture()
