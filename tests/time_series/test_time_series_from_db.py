#!/usr/bin/env python
# -*- coding: utf-8 mode: python -*-

# test_time_series.py - Unit test module to test the time_series class
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
import pickle
import unittest
import time_series
import sticker_core.symbol as symbol

# ---------------------------------------------------------------
class TestTimeSeries(unittest.TestCase):

    # -----------------------------------------------------------
    def setUp(self):
        self.db = anydbm.open('test_time_series.db', 'r')

        self.m_start = self.db[ 'm_start' ]
        self.end = self.db[ 'end' ]
        self.ts_1 = pickle.loads(self.db['time_series_1'])





    # -----------------------------------------------------------
    def test_max(self):
        print "Running test_max"
        self.assertAlmostEqual(self.ts_1.max(self.m_start, self.end),
                               pickle.loads(self.db['max']))

    # -----------------------------------------------------------
    def test_min(self):
        print "Running test_min"
        self.assertAlmostEqual(self.ts_1.min(self.m_start, self.end),
                               pickle.loads(self.db['min']))

    # -----------------------------------------------------------
    def test_sum(self):
        print "Running test_sum"
        self.assertAlmostEqual(self.ts_1.sum(self.m_start, self.end),
                               pickle.loads(self.db['sum']))

    # -----------------------------------------------------------
    def test_m_sum(self):
        print "Running test_m_sum"
        calculated = self.ts_1.m_sum(self.m_start, self.end, 10)
        from_db    = pickle.loads(self.db['m_sum'])

        for i in range(0, len(from_db.data)):
            self.assertAlmostEqual(calculated.data[i], from_db.data[i])
            self.assertEqual(calculated.times[i], from_db.times[i])

    # -----------------------------------------------------------
    def test_avg(self):
        print "Running test_avg"
        self.assertAlmostEqual(self.ts_1.avg(self.m_start, self.end),
                               pickle.loads(self.db['avg']))

    # -----------------------------------------------------------
    def test_m_avg(self):
        print "Running test_m_avg"
        calculated = self.ts_1.m_avg(self.m_start, self.end, 10)
        from_db    = pickle.loads(self.db['m_avg'])

        for i in range(0, len(from_db.data)):
            self.assertAlmostEqual(calculated.data[i], from_db.data[i])
            self.assertEqual(calculated.times[i], from_db.times[i])

    # -----------------------------------------------------------
    def test_exp_m_avg(self):
        print "Running test_exp_m_avg (uses a user specified seed)"
        calculated = self.ts_1.exp_m_avg(self.m_start, self.end, 10)
        from_db    = pickle.loads(self.db['exp_m_avg'])

        for i in range(0, len(from_db.data)):
            self.assertAlmostEqual(calculated.data[i], from_db.data[i])
            self.assertEqual(calculated.times[i], from_db.times[i])        

    # -----------------------------------------------------------
    def test_hist_changes(self):
        print "Running test_hist_changes"
        calculated = self.ts_1.hist_changes(self.m_start, self.end, 1)
        from_db    = pickle.loads(self.db['hist_changes'])

        for i in range(0, len(from_db.data)):
            self.assertAlmostEqual(calculated.data[i], from_db.data[i])
            self.assertEqual(calculated.times[i], from_db.times[i])        

    # -----------------------------------------------------------
    def test_hist_adv(self):
        print "Running test_hist_adv"
        calculated = self.ts_1.hist_adv(self.m_start, self.end, 1)
        from_db    = pickle.loads(self.db['hist_adv'])

        for i in range(0, len(from_db.data)):
            self.assertAlmostEqual(calculated.data[i], from_db.data[i])
            self.assertEqual(calculated.times[i], from_db.times[i])         

    # -----------------------------------------------------------
    def test_hist_dec(self):
        print "Running test_hist_dec"
        calculated = self.ts_1.hist_dec(self.m_start, self.end, 1)
        from_db    = pickle.loads(self.db['hist_dec'])

        for i in range(0, len(from_db.data)):
            self.assertAlmostEqual(calculated.data[i], from_db.data[i])
            self.assertEqual(calculated.times[i], from_db.times[i])         

    # -----------------------------------------------------------
    def test_rsi(self):
        print "Running test_rsi"
        calculated = self.ts_1.rsi(self.m_start,self.end, 10)
        from_db    = pickle.loads(self.db['rsi'])

        for i in range(0, len(from_db.data)):
            self.assertAlmostEqual(calculated.data[i], from_db.data[i])
            self.assertEqual(calculated.times[i], from_db.times[i])         

    # -----------------------------------------------------------
    def test_exp_rsi(self):
        print "Running test_exp_rsi"
        calculated = self.ts_1.exp_rsi(self.m_start,self.end, 10)
        from_db = pickle.loads(self.db['exp_rsi'])

        for i in range(0, len(from_db.data)):
            self.assertAlmostEqual(calculated.data[i], from_db.data[i])
            self.assertEqual(calculated.times[i], from_db.times[i])         

    # -----------------------------------------------------------
    def test_stdev(self):
        print "Running test_stdev"
        calculated = self.ts_1.stdev(self.m_start, self.end, 10)
        from_db = pickle.loads(self.db['stdev'])

        for i in range(0, len(from_db.data)):
            self.assertAlmostEqual(calculated.data[i], from_db.data[i])
            self.assertEqual(calculated.times[i], from_db.times[i])

    # -----------------------------------------------------------
    def test_b_bands(self):
        print "Running test_b_bands"
        calculated = self.ts_1.b_bands(self.m_start, self.end, 10, 2)
        from_db    = pickle.loads(self.db['b_bands'])

        for i in range(0, len(from_db)):
            for j in range(0, len(from_db[i].data)):
                self.assertAlmostEqual(calculated[i].data[j],from_db[i].data[j])
                self.assertEqual(calculated[i].times[j], from_db[i].times[j])

    # -----------------------------------------------------------
    def test_low(self):
        print "Running test_low"
        calculated = self.ts_1.low(self.m_start, self.end, 1)
        from_db    = pickle.loads(self.db['low'])

        for i in range(0, len(from_db.data)):
            self.assertAlmostEqual(calculated.data[i], from_db.data[i])
            self.assertEqual(calculated.times[i], from_db.times[i])

    # -----------------------------------------------------------
    def test_high(self):
        print "Running test_high"
        calculated = self.ts_1.high(self.m_start, self.end, 1)
        from_db    = pickle.loads(self.db['high'])

        for i in range(0, len(from_db.data)):
            self.assertAlmostEqual(calculated.data[i], from_db.data[i])
            self.assertEqual(calculated.times[i], from_db.times[i])

    # -----------------------------------------------------------
    def test_fsto_k(self):
        print "Running test_fsto_k"

    # -----------------------------------------------------------
    def test_money_flow_index(self):
        print "Running test_money_flow_index"

    # -----------------------------------------------------------
    def test_monotonous_up(self):
        print "Running test_monotonous_up"
        self.assertEqual(self.ts_1.monotonous_up(self.end,10),
                         pickle.loads(self.db['monotonous_up']))

    # -----------------------------------------------------------
    def test_monotonous_down(self):
        print "Running test_monotonous_down"
        self.assertEqual(self.ts_1.monotonous_down(self.end,10),
                         pickle.loads(self.db['monotonous_down']))


    # -----------------------------------------------------------
    def test_historic_spread(self):
        print "Running test_historic_spread"
        self.assertAlmostEqual(self.ts_1.historic_spread(self.end,10),
                               pickle.loads(self.db['historic_spread']))

    # -----------------------------------------------------------
    def test_roc(self):
        print "Running test_roc"
        self.assertAlmostEqual(self.ts_1.roc(self.end,10),
                               pickle.loads(self.db['roc']))

    # -----------------------------------------------------------
    def test_derivatve(self):
        print "Running test_derivative"
        calculated = self.ts_1.derivative(self.m_start, self.end)
        from_db    = pickle.loads(self.db['derivative'])

        for i in range(0, len(from_db.data)):
            self.assertAlmostEqual(calculated.data[i], from_db.data[i])
            self.assertEqual(calculated.times[i], from_db.times[i])

    # -----------------------------------------------------------
    def test_derivatve_m_avg(self):
        print "Running test_derivative_m_avg"
        calculated = self.ts_1.derivative_m_avg(self.m_start, self.end, 10)
        from_db    = pickle.loads(self.db['derivative_m_avg'])

        for i in range(0, len(from_db.data)):
            self.assertAlmostEqual(calculated.data[i], from_db.data[i])
            self.assertEqual(calculated.times[i], from_db.times[i])

            


# ---------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

