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

import unittest
import time_series
import math
import sticker_core.symbol as symbol

# ---------------------------------------------------------------
class TestTimeSeries(unittest.TestCase):

    # -----------------------------------------------------------
    def setUp(self):
        self.test_symbol = symbol.Symbol('^DJI', '20090103', '20091001')

        self.time_series1 = time_series.TimeSeries(
            [ '20090101', '20090102', '20090103', '20090104'],
            [       1000,       1001,       1002,      1003 ])
        self.time_series2 = time_series.TimeSeries(
            [ '20090101', '20090102', '20090103', '20090104'],
            [       1000,       998,       1002,      1003 ])
        self.time_series3 = time_series.TimeSeries(
            [ '20090101', '20090102', '20090103', '20090104'],
            [       1003,      1002,       1001,      1000 ])

        self.time_series_long = time_series.TimeSeries(
            [ '20090101', '20090102', '20090103', '20090104',
              '20090105', '20090106', '20090107', '20090108',
              '20090109', '20090110', '20090111', '20090112',
              '20090113', '20090114', '20090115', '20090116',],
            [       1000,       998,        970,      1008,
                    1001,       978,        999,      1002,
                    1005,      1002,        998,      1000,
                    999,      1002,       1004,      1007,])

        self.time_series_m_avg = time_series.TimeSeries(
            [ '20090102', '20090103', '20090104'],
            [     1000.5,     1001.5,    1002.5 ])

        self.time_series_hist_changes = time_series.TimeSeries(
            [ '20090102', '20090103', '20090104'],
            [         -2,          4,         1 ])
        self.time_series_hist_adv = time_series.TimeSeries(
            [ '20090102', '20090103', '20090104'],
            [          0,          4,         1 ])
        self.time_series_hist_dec = time_series.TimeSeries(
            [ '20090102', '20090103', '20090104'],
            [          2,          0,         0 ])

        self.time_series_low1 = time_series.TimeSeries(
            [ '20090110', '20090111', '20090112'],
            [       1002,        998,      1000 ])
        self.time_series_low2 = time_series.TimeSeries(
            [ '20090110', '20090111', '20090112'],
            [       1002,        998,      998 ])
        self.time_series_low8 = time_series.TimeSeries(
            [ '20090110', '20090111', '20090112'],
            [       970,        978,      978 ])
        self.time_series_high1 = time_series.TimeSeries(
            [ '20090110', '20090111', '20090112'],
            [       1002,        998,      1000 ])
        self.time_series_high2 = time_series.TimeSeries(
            [ '20090110', '20090111', '20090112'],
            [       1005,       1002,     1000 ])
        self.time_series_high8 = time_series.TimeSeries(
            [ '20090110', '20090111', '20090112'],
            [       1008,       1008,     1005 ])
        self.time_series_rsi = time_series.TimeSeries(
            ['0', '1', '2', '3', '4',
             '5', '6', '7', '8',
             '9', '10','11','12',
             '13','14','15','16',
             '17','18','19'],
            [46.125, 47.125,  46.4375, 46.9375, 44.9375,
             44.25,   44.625,  45.75,   47.8125,
             47.5625, 47.0,    44.5625, 46.3125,
             47.6875, 46.6875, 45.6875, 43.0625,
             43.5625, 44.875,  43.6875])

        self.time_series_stdev = time_series.TimeSeries(
            ['20090901', '20090902', '20090903', '20090904',
              '20090905', '20090906', '20090907', '20090908'],
            [ 2.,4.,4.,4.,5.,5.,7.,9.])

        self.time_series_exp_m_avg = time_series.TimeSeries(
            ['1', '2', '3', '4',
             '5', '6', '7', '8',
             '9', '10','11','12',
             '13','14','15','16',
             '17','18','19','20'],
            [64.75,63.79,63.73,63.73,
             63.55,63.19,63.91,63.85,
             62.95,63.37,61.33,61.51,
             61.87,60.25,59.35,59.95,
             58.93,57.68,58.82,58.87])


    # -----------------------------------------------------------
    def test_max(self):
        print "Running test_max"
        self.assertEqual(self.time_series1.max('20090101','20090104'), 1003)

    # -----------------------------------------------------------
    def test_min(self):
        print "Running test_min"
        self.assertEqual(self.time_series1.min('20090101','20090104'), 1000)

    # -----------------------------------------------------------
    def test_sum(self):
        print "Running test_sum"
        self.assertEqual(self.time_series1.sum('20090101','20090101'), 1000)
        self.assertEqual(self.time_series1.sum('20090101','20090104'), 4006)

    # -----------------------------------------------------------
    def test_m_sum(self):
        print "Running test_m_sum"
        self.assertEqual(self.time_series_long.m_sum('20090101','20090116', 1).data,
                         self.time_series_long.data)
        self.assertEqual(self.time_series_long.m_sum('20090114','20090116', 3).data,
                         [3001, 3005, 3013])

    # -----------------------------------------------------------
    def test_avg(self):
        print "Running test_avg"
        self.assertEqual(self.time_series1.avg('20090101','20090101'), 1000)
        self.assertEqual(self.time_series1.avg('20090104','20090104'), 1003)
        self.assertEqual(self.time_series1.avg('20090101','20090104'), 1001.5)

    # -----------------------------------------------------------
    def test_m_avg(self):
        print "Running test_m_avg"
        list = [1000.5, 1001.5, 1002.5]
        m_avg = self.time_series1.m_avg('20090102','20090104', 2).data
        for i in range(0,len(m_avg)):
            self.assertAlmostEqual(m_avg[i], list[i])

    # -----------------------------------------------------------
    def test_exp_m_avg(self):
        print "Running test_exp_m_avg (uses a user specified seed)"
        list = [63.2543636364, 62.9372066116, 62.7431690458, 62.2898655830,
                61.7553445679, 61.4271001010, 60.9730819008, 60.3743397370,
                60.0917325121, 59.8695993281]
        exp_m_avg = self.time_series_exp_m_avg.exp_m_avg('11','20',10,63.6820000000).data
        for i in range(0,len(exp_m_avg)):
            self.assertAlmostEqual(exp_m_avg[i], list[i])

    # -----------------------------------------------------------
    def test_hist_changes(self):
        print "Running test_hist_changes"
        hist_changes_data = self.time_series2.hist_changes('20090102','20090104').data
        self.assertEqual(hist_changes_data, self.time_series_hist_changes.data)

    # -----------------------------------------------------------
    def test_hist_adv(self):
        print "Running test_hist_adv"
        hist_adv_data = self.time_series2.hist_adv('20090102','20090104').data
        self.assertEqual(hist_adv_data, self.time_series_hist_adv.data)

    # -----------------------------------------------------------
    def test_hist_dec(self):
        print "Running test_hist_dec"
        hist_dec_data = self.time_series2.hist_dec('20090102','20090104').data
        self.assertEqual(hist_dec_data, self.time_series_hist_dec.data)

    # -----------------------------------------------------------
    def test_rsi(self):
        print "Running test_rsi"
        list = [51.778656126482, 45.454545454546, 40.492957746479,
                40.492957746479, 49.816849816850, 48.398576512456]

        rsi = self.time_series_rsi.rsi('14','19', 14).data
        for i in range(0, len(rsi)):
            self.assertAlmostEqual(rsi[i], list[i])

    # -----------------------------------------------------------
    def test_exp_rsi(self):
        print "Running NONEXISTANT test_exp_rsi"

    # -----------------------------------------------------------
    def test_stdev(self):
        print "Running test_stdev"
        list= [0.86602540378444, 0.43301270189222, 0.5, 1.0897247358852,
               1.6583123951777]

        stdev= self.time_series_stdev.stdev('20090904','20090908',4).data
        for i in range(0,len(stdev)):
            self.assertAlmostEqual(stdev[i], list[i])

    # -----------------------------------------------------------
    def test_b_bands(self):
        print "Running NONEXISTANT test_b_bands"

    # -----------------------------------------------------------
    def test_low(self):
        print "Running test_low"
        low1_data = self.time_series_long.low('20090110','20090112', 1).data
        low2_data = self.time_series_long.low('20090110','20090112', 2).data
        low8_data = self.time_series_long.low('20090110','20090112', 8).data
        self.assertEqual(low1_data, self.time_series_low1.data)
        self.assertEqual(low2_data, self.time_series_low2.data)
        self.assertEqual(low8_data, self.time_series_low8.data)

    # -----------------------------------------------------------
    def test_high(self):
        print "Running test_high"
        high1_data = self.time_series_long.high('20090110','20090112', 1).data
        high2_data = self.time_series_long.high('20090110','20090112', 2).data
        high8_data = self.time_series_long.high('20090110','20090112', 8).data
        self.assertEqual(high1_data, self.time_series_high1.data)
        self.assertEqual(high2_data, self.time_series_high2.data)
        self.assertEqual(high8_data, self.time_series_high8.data)

    # -----------------------------------------------------------
    def test_fsto_k(self):
        print "Running test_fsto_k"
        low8  = self.time_series_long.low('20090110','20090112', 8)
        high8 = self.time_series_long.high('20090110','20090112', 8)
        fsto_k = self.time_series_long.fsto_k(low8, high8, '20090110','20090112', 8).data

    # -----------------------------------------------------------
    def test_money_flow_index(self):
        print "Running test_money_flow_index"
        mfi = self.test_symbol.close.mfi(self.test_symbol.high,  self.test_symbol.low,
                                         self.test_symbol.close, self.test_symbol.volume,
                                         '20091001', '20091001', 4)
        # self.assertAlmostEqual(mfi.data[0], 68.4884868)

    # -----------------------------------------------------------
    def test_monotonous_up(self):
        print "Running test_monotonous_up"
        self.assertEqual(True,  self.time_series1.monotonous_up('20090104', 3))
        self.assertEqual(False, self.time_series2.monotonous_up('20090104', 3))

    # -----------------------------------------------------------
    def test_monotonous_down(self):
        print "Running test_monotonous_down"
        self.assertEqual(False,  self.time_series1.monotonous_down('20090104', 3))
        self.assertEqual(True,   self.time_series3.monotonous_down('20090104', 3))

    # -----------------------------------------------------------
    def test_historic_spread(self):
        print "Running test_historic_spread"
        self.assertEqual(38,  self.time_series_long.historic_spread('20090116', 14))


# ---------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

