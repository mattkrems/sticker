#!/usr/bin/env python
# -*- coding: utf-8 mode: python -*-

# time_series.py - Basic class to compute properties of time series.
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
import math

# ---------------------------------------------------------------
class TimeSeries:
    # -----------------------------------------------------------
    def __init__(self, times, data):
        self.data = data            # list of data
        self.time_hash = {}
        self.times = times          # list of corresponding times associated with data
        for i in range(0, len(self.times)):
            self.time_hash [ self.times[i]  ] = i
        self.start_date = times[0]
        self.end_date = times[-1]

    # -----------------------------------------------------------
    def _get_index(self, point):
        try:
            index = self.time_hash[ point ]
        except:
            index = None
        return index

    # -----------------------------------------------------------
    def _cut_list(self, start_point, end_point, type):
        start_index = self._get_index(start_point)
        end_index = self._get_index(end_point)
        if type == 'data':
            return self.data[start_index:end_index + 1]
        elif type == 'times':
            return self.times[start_index:end_index + 1]

    # -----------------------------------------------------------
    def _check_validity(self, point):
        if self._get_index(point) == None:
            print "ERROR: Invalid Point - ", point
            return False
        else:
            return True

    # -----------------------------------------------------------
    def get_index(self, point):
        return self._get_index(point)

    # -----------------------------------------------------------
    def max(self, start_point, end_point):
        if self._check_validity(start_point) == False: return
        if self._check_validity(end_point)   == False: return

        return max(self._cut_list(start_point, end_point, 'data'))

    # -----------------------------------------------------------
    def min(self, start_point, end_point):
        if self._check_validity(start_point) == False: return
        if self._check_validity(end_point)   == False: return

        return min(self._cut_list(start_point, end_point, 'data'))

    # -----------------------------------------------------------
    def sum(self, start_point, end_point):
        if self._check_validity(start_point) == False: return
        if self._check_validity(end_point)   == False: return

        return sum(self._cut_list(start_point, end_point, 'data'))

    # -----------------------------------------------------------
    def m_sum(self, start_point, end_point, m_avg_len=1):
        if self._check_validity(start_point) == False: return
        if self._check_validity(end_point)   == False: return
        start_index = self._get_index(start_point)
        end_index = self._get_index(end_point)

        m_sum = []
        for i in range(start_index, end_index+1):
            m_sum.append(self.sum(self.times[i-m_avg_len+1], self.times[i]))

        return TimeSeries(self._cut_list(start_point, end_point, 'times'), m_sum)

    # -----------------------------------------------------------
    def avg(self, start_point, end_point):
        if self._check_validity(start_point) == False: return
        if self._check_validity(end_point)   == False: return
        start_index = self._get_index(start_point)
        end_index = self._get_index(end_point)

        sum = 0.0
        for i in range(start_index, end_index+1):
            sum = sum + self.data[i]

        return sum/(end_index - start_index + 1)

    # -----------------------------------------------------------
    def m_avg(self, start_point, end_point, m_avg_len=1):
        if self._check_validity(start_point) == False: return
        if self._check_validity(end_point)   == False: return
        start_index = self._get_index(start_point)
        end_index = self._get_index(end_point)

        m_avg = []
        for i in range(start_index, end_index+1):
            m_avg.append(self.avg(self.times[i-m_avg_len+1], self.times[i]))

        return TimeSeries(self._cut_list(start_point, end_point, 'times'), m_avg)

    # -----------------------------------------------------------
    def _get_exp_m_avg_seed(self, start_point, exp_m_avg_len):
        settle_factor = 10*exp_m_avg_len

        start_index = self._get_index(start_point)

        seed_index=self._get_index(start_point)-1 - settle_factor
        temp = self.avg(self.times[seed_index - exp_m_avg_len + 1],
                        self.times[seed_index])

        k = 2.0/(exp_m_avg_len + 1)
        for i in range(seed_index+1, start_index):
            temp = self.data[i]*k + temp * (1-k)

        return temp

    # -----------------------------------------------------------
    def exp_m_avg(self, start_point, end_point, exp_m_avg_len, seed=None):
        if self._check_validity(start_point) == False: return
        if self._check_validity(end_point)   == False: return
        start_index = self._get_index(start_point)
        end_index = self._get_index(end_point)

        if seed == None:
            temp = self._get_exp_m_avg_seed(start_point, exp_m_avg_len)
        else:
            temp = seed

        k = 2.0/(exp_m_avg_len + 1)
        exp_m_avg = []
        for i in range(start_index, end_index+1):
            temp = self.data[i]*k + temp * (1-k)
            if i >= start_index:
                exp_m_avg.append(temp)

        return TimeSeries(self._cut_list(start_point, end_point, 'times'), exp_m_avg)

    # -----------------------------------------------------------
    def hist_changes(self, start_point, end_point, hist_len=1):
        if self._check_validity(start_point) == False: return
        if self._check_validity(end_point)   == False: return

        start_index = self._get_index(start_point)
        end_index = self._get_index(end_point)

        hist_changes = []
        for i in range(start_index, end_index + 1):
            hist_changes.append(self.data[i]-self.data[i-hist_len])

        return TimeSeries(self._cut_list(start_point, end_point, 'times'), hist_changes)

    # -----------------------------------------------------------
    def hist_adv(self, start_point, end_point, hist_len=1):
        if self._check_validity(start_point) == False: return
        if self._check_validity(end_point)   == False: return

        temp = self.hist_changes(start_point, end_point, hist_len)
        for i in range(0,len(temp.data)):
            if temp.data[i] < 0:
                temp.data[i] = 0

        return temp

    # -----------------------------------------------------------
    def hist_dec(self, start_point, end_point, hist_len=1):
        if self._check_validity(start_point) == False: return
        if self._check_validity(end_point)   == False: return

        temp = self.hist_changes(start_point, end_point, hist_len)
        for i in range(0,len(temp.data)):
            if temp.data[i] < 0:
                temp.data[i] = abs(temp.data[i])
            elif temp.data[i] > 0:
                temp.data[i] = 0

        return temp

    # -----------------------------------------------------------
    def rsi(self, start_point, end_point, m_avg_len):
        if self._check_validity(start_point) == False: return
        if self._check_validity(end_point)   == False: return
        start_index = self._get_index(start_point)

        #get enough hist_adv and hist_dec to calculate a m_avg of them
        hist_adv = self.hist_adv(self.times[start_index-m_avg_len+1],
                                 end_point)
        hist_dec = self.hist_dec(self.times[start_index-m_avg_len+1],
                                 end_point)

        #get m_avg of advances and declines
        ma_adv = hist_adv.m_avg(start_point, end_point, m_avg_len).data
        ma_dec = hist_dec.m_avg(start_point, end_point, m_avg_len).data

        rsi = []
        for i in range(0, len(ma_adv)):
            if ma_dec[i] != 0:
                rs = ma_adv[i]/ma_dec[i]
                rsi.append(100- 100*1.0/(1+rs))
            else:
                rsi.append(100)

        return TimeSeries(self._cut_list(start_point, end_point, 'times'), rsi)

    # -----------------------------------------------------------
    def exp_rsi(self, start_point, end_point, exp_m_avg_len):
        settle_factor = 10*exp_m_avg_len + exp_m_avg_len

        if self._check_validity(start_point) == False: return
        if self._check_validity(end_point)   == False: return
        start_index = self._get_index(start_point)

        #get enough hist_adv and hist_dec to calculate a m_avg of them
        hist_adv = self.hist_adv(self.times[start_index - settle_factor],
                                 end_point)
        hist_dec = self.hist_dec(self.times[start_index - settle_factor],
                                 end_point)

        #get m_avg of advances and declines
        ema_adv = hist_adv.exp_m_avg(start_point, end_point, exp_m_avg_len).data
        ema_dec = hist_dec.exp_m_avg(start_point, end_point, exp_m_avg_len).data

        rsi = []
        for i in range(0, len(ema_adv)):
            if ema_dec[i] != 0:
                rs = ema_adv[i]/ema_dec[i]
                rsi.append(100- 100*1.0/(1+rs))
            else:
                rsi.append(100)

        return TimeSeries(self._cut_list(start_point, end_point, 'times'), rsi)

    # -----------------------------------------------------------
    def stdev(self, start_point, end_point, stdev_len):
        if self._check_validity(start_point) == False: return
        if self._check_validity(end_point)   == False: return
        start_index = self._get_index(start_point)
        end_index = self._get_index(end_point)

        sigma = []
        for i in range(start_index, end_index+1):
            mean = self.avg(self.times[i-stdev_len+1], self.times[i])
            sum = 0.
            for j in range(i - stdev_len+1, i+1):
                sum = sum + math.pow((self.data[j] - mean),2)
            sigma.append(math.sqrt(sum/stdev_len))

        return TimeSeries(self._cut_list(start_point, end_point, 'times'), sigma)

    # -----------------------------------------------------------
    def b_bands(self, start_point, end_point, bb_len=20, num_stdev=2):
        if self._check_validity(start_point) == False: return
        if self._check_validity(end_point)   == False: return

        m_avg = self.m_avg(start_point, end_point, bb_len)
        stdev = self.stdev(start_point, end_point, bb_len)

        upper = []
        lower = []
        for i in range(0, len(m_avg.data)):
            upper.append(m_avg.data[i] + num_stdev*stdev.data[i])
            lower.append(m_avg.data[i] - num_stdev*stdev.data[i])

        upper = TimeSeries(self._cut_list(start_point, end_point, 'times'), upper)
        lower = TimeSeries(self._cut_list(start_point, end_point, 'times'), lower)
        return upper, m_avg, lower

    # -----------------------------------------------------------
    def low(self, start_point, end_point, hist_len=1):
        if self._check_validity(start_point) == False: return
        if self._check_validity(end_point)   == False: return


        start_index = self._get_index(start_point) - hist_len + 1
        current_index = self._get_index(start_point)
        delta_index = self._get_index(end_point) - current_index
        low = []
        for i in range(0, delta_index+1):
            if len(self.data[start_index + i:current_index + i + 1]) > 0:
                low.append(min(self.data[start_index + i:current_index + i + 1]))
        return TimeSeries(self._cut_list(start_point, end_point, 'times'), low)

    # -----------------------------------------------------------
    def high(self, start_point, end_point, hist_len=1):
        if self._check_validity(start_point) == False: return
        if self._check_validity(end_point)   == False: return

        start_index = self._get_index(start_point) - hist_len + 1
        current_index = self._get_index(start_point)
        delta_index = self._get_index(end_point) - current_index
        high = []
        for i in range(0, delta_index+1):
            if len(self.data[start_index + i:current_index + i + 1]) > 0:
                high.append(max(self.data[start_index + i:current_index + i + 1]))
        return TimeSeries(self._cut_list(start_point, end_point, 'times'), high)

    # -----------------------------------------------------------
    def fsto_k(self, low, high, start_point, end_point, hist_len=1):
        if self._check_validity(start_point) == False: return
        if self._check_validity(end_point)   == False: return
        if low._check_validity(start_point)  == False: return
        if low._check_validity(end_point)    == False: return
        if high._check_validity(start_point) == False: return
        if high._check_validity(end_point)   == False: return

        start_index = self._get_index(start_point)
        end_index = self._get_index(end_point)
        fsto_k = []
        for i in range(start_index, end_index + 1):
            sl = low.data[i - start_index]
            sh = high.data[i - start_index]
            if sh - sl == 0:
                fsto_k.append(100)
            else:
                fsto_k.append(100 * (self.data[i] - sl) / (sh - sl))
        return TimeSeries(self._cut_list(start_point, end_point, 'times'), fsto_k)

    # -----------------------------------------------------------
    def mfi(self, high, low, close, volume, start_point, end_point, m_sum_len):
        if self._check_validity(start_point)   == False: return
        if self._check_validity(end_point)     == False: return
        if low._check_validity(start_point)    == False: return
        if low._check_validity(end_point)      == False: return
        if high._check_validity(start_point)   == False: return
        if high._check_validity(end_point)     == False: return
        if close._check_validity(start_point)  == False: return
        if close._check_validity(end_point)    == False: return
        if volume._check_validity(start_point) == False: return
        if volume._check_validity(end_point)   == False: return

        start_index = self._get_index(start_point)
        end_index = self._get_index(end_point)

        # calculate hist_adv and hist_dec
        close_hist_adv = self.hist_adv(self.times[start_index-m_sum_len+1], end_point)
        close_hist_dec = self.hist_dec(self.times[start_index-m_sum_len+1], end_point)

        # compute raw money flow
        rmf_hist_adv = TimeSeries(self.times[start_index-m_sum_len+1:end_index+1], [])
        rmf_hist_dec = TimeSeries(self.times[start_index-m_sum_len+1:end_index+1], [])
        for i in range(start_index-m_sum_len+1, end_index + 1):
            typical_price = (high.data[i] + low.data[i] + close.data[i]) / 3.0
            if close_hist_adv.data[i - (start_index - m_sum_len + 1)] > 0:
                rmf_hist_adv.data.append(typical_price * volume.data[i])
            else:
                rmf_hist_adv.data.append(0)
            if close_hist_dec.data[i - (start_index - m_sum_len + 1)] > 0:
                rmf_hist_dec.data.append(typical_price * volume.data[i])
            else:
                rmf_hist_dec.data.append(0)


        # get m_sum of advances and declines
        rmf_ms_adv = rmf_hist_adv.m_sum(start_point, end_point, m_sum_len).data
        rmf_ms_dec = rmf_hist_dec.m_sum(start_point, end_point, m_sum_len).data

        mfi = []
        for i in range(0, len(rmf_ms_adv)):
            if rmf_ms_dec[i] != 0:
                money_ratio = rmf_ms_adv[i]/rmf_ms_dec[i]
                mfi.append(100. - 100./(1. + money_ratio))
            else:
                mfi.append(100)
        return TimeSeries(self._cut_list(start_point, end_point, 'times'), mfi)

    # -----------------------------------------------------------
    def monotonous_up(self, date, range_hist_len=1):
        if self._check_validity(date) == False: return

        end_index   = self._get_index(date)
        start_index = end_index - range_hist_len
        if start_index < 0:
            print "ERROR: time series to short for range parameter ",
            return False

        monotonous_up = True
        for i in range(start_index + 1, end_index + 1):
            monotonous_up = monotonous_up and self.data[i-1] < self.data[i]
        return monotonous_up

    # -----------------------------------------------------------
    def monotonous_down(self, date, range_hist_len=1):
        if self._check_validity(date) == False: return

        end_index   = self._get_index(date)
        start_index = end_index - range_hist_len
        if start_index < 0:
            print "ERROR: time series to short for range parameter ",
            return False

        monotonous_down = True
        for i in range(start_index + 1, end_index + 1):
            monotonous_down = monotonous_down and self.data[i-1] > self.data[i]
        return monotonous_down

    # -----------------------------------------------------------
    def historic_spread(self, date, range_hist_len=1):
        if self._check_validity(date) == False: return

        end_index   = self._get_index(date)
        start_index = end_index - range_hist_len
        if start_index < 0:
            print "ERROR: time series to short for range parameter ",
            return False

        hist_min = self.data[start_index]
        hist_max = self.data[start_index]
        for i in range(start_index+1, end_index + 1):
            hist_min = min([hist_min, self.data[i]])
            hist_max = max([hist_max, self.data[i]])
        return hist_max - hist_min

    # -----------------------------------------------------------
    def roc(self, date, range_hist_len=1):
        if self._check_validity(date) == False: return

        end_index   = self._get_index(date)
        start_index = end_index - range_hist_len
        if start_index < 0:
            print "ERROR: time series to short for range parameter ",
            return False

        roc = (self.data[end_index] - self.data[start_index])/self.data[start_index] * 100
        return roc

    # -----------------------------------------------------------
    def derivative(self, start_point, end_point):
        if self._check_validity(start_point) == False: return
        if self._check_validity(end_point)   == False: return
        start_index = self._get_index(start_point)
        end_index = self._get_index(end_point)
        
        derivative = []
        for i in range(start_index, end_index+1):
            #print self.data
            #print self.times
            #if i <= end_index-2:
            #    derivative.append((-self.data[i+2]+8*self.data[i+1] \
            #                           -8*self.data[i-1]+self.data[i-2])/12.0)
            
            derivative.append((3*self.data[i] - 4*self.data[i-1] + self.data[i-2])/2.0)

        return TimeSeries(self._cut_list(start_point, end_point, 'times'), derivative)

    # -----------------------------------------------------------
    def derivative_m_avg(self, start_point, end_point, m_avg_len):
        if self._check_validity(start_point) == False: return
        if self._check_validity(end_point)   == False: return
        start_index = self._get_index(start_point)-m_avg_len+1
        end_index = self._get_index(end_point)

        m_avg=self.m_avg(self.times[start_index], end_point, m_avg_len)

        return m_avg.derivative(start_point, end_point)
