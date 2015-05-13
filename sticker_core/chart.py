#!/usr/bin/env python
# -*- coding: utf-8 mode: python -*-

# add_symbol.py - Module to add symbols to the database
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

import pylab
import pdb
import numpy
import datetime
import matplotlib.dates as mdates
import matplotlib.collections as collections

class Chart:
    def __init__(self, symbol, trading_strategy=None): 
        self.ts = trading_strategy
        self.symbol = symbol.symbol

        self.times = []
        self.data = []

        self.sub_times = []
        self.sub_data = []

    def add_main_plot(self, TimeSeries):
        times = []
        for d in TimeSeries.times:
            times.append(self._convert_to_datetime(d))
        self.times.append(numpy.array(times))
        self.data.append(numpy.float64(TimeSeries.data))
    
    def add_subplot(self, TimeSeries):
        times = []
        for d in TimeSeries.times:
            times.append(self._convert_to_datetime(d))
        self.sub_times.append(numpy.array(times))
        self.sub_data.append(numpy.float64(TimeSeries.data))

    def show(self):
        if self.ts != None:
            start = self.ts.trading_days[0]
            end = self.ts.trading_days[-1]

            u, mid, l = self.ts.trading_symbols.components[self.symbol].close.b_bands(start, end, 20)
            self.add_main_plot(self.ts.trading_symbols.components[self.symbol].close)
            self.add_main_plot(u)
            self.add_main_plot(mid)
            self.add_main_plot(l)
            self.add_subplot(self.ts.trading_symbols.components[self.symbol].close.rsi(start, end, 6))

        self._make_figure()
        pylab.show()  

    def savefig(self, filename):
        if self.ts != None:
            start = self.ts.trading_days[0]
            end = self.ts.trading_days[-1]

            u, mid, l = self.ts.trading_symbols.components[self.symbol].close.b_bands(start, end, 20)
            self.add_main_plot(self.ts.trading_symbols.components[self.symbol].close)
            self.add_main_plot(u)
            self.add_main_plot(mid)
            self.add_main_plot(l)
            self.add_subplot(self.ts.trading_symbols.components[self.symbol].close.rsi(start, end, 6))
            # need to be able to pass y-axis range?
            self.add_subplot(self.ts.performance_index[ 'p_index' ])

        self._make_figure()
        pylab.savefig(filename, dpi=100, format='png')
    
    def _make_figure(self):
        num_sub_plots = len(self.sub_data)
        sub_rect = []
        if num_sub_plots ==0:
            fig = pylab.figure()
        if num_sub_plots == 1:
            w, h = pylab.figaspect(0.5)
            fig = pylab.figure(figsize=(w,h))
            main_rect = [0.20, 0.23, 0.78, 0.72]
            sub_rect.append([0.20, 0.09, 0.78, 0.12])
        if num_sub_plots == 2:
            w, h = 1.4*pylab.figaspect(0.7)
            fig = pylab.figure(figsize=(w,h))
            main_rect = [0.20, 0.35, 0.78, 0.62]
            sub_rect.append([0.20, 0.09, 0.78, 0.12])
            sub_rect.append([0.20, 0.22, 0.78, 0.12])
            

        fig = self._make_main_plot(fig, main_rect)
        if num_sub_plots > 0:
            fig = self._make_sub_plot(fig, sub_rect)
        self._add_text(fig)

    def _make_main_plot(self, fig, rect):
        ax = fig.add_axes(rect)

        for i in range(0, len(self.data)):
            ax.plot(self.times[i],self.data[i], lw=0.6)

        #turn off xlabels and first ylabel if there is a subplot
        if len(self.sub_times) > 0:
            for label in ax.get_xticklabels():
                label.set_visible(False)
            
            label = ax.get_yticklabels()
            label[0].set_visible(False)

        #formatting options
        self._format_x_axis(ax)
        def price(x): return '$%1.2f'%x
        ax.format_ydata = price
        ax.grid(True)
 
        if self.ts != None: self._add_in_n_out([ax])
        return fig

    def _make_sub_plot(self, fig, rect_list):
        ax = []
        for i in rect_list:
            ax.append(fig.add_axes(i))
    
        for i in range(0, len(self.sub_data)):
            ax[i].plot(self.sub_times[i],self.sub_data[i], lw=0.6)

            if i == len(self.sub_data) -1 and i > 0:
                for label in ax[i].get_xticklabels():
                    label.set_visible(False)

        #formatting options
        for i in ax:              
            self._format_x_axis(i)
            i.grid(True)
            i.set_ylim(0,100)
        
        if self.ts != None: self._add_in_n_out(ax)
        return fig

    def _add_in_n_out(self, ax_list): 
        start = None
        for ax in ax_list:
            for i in range(0, len(self.ts.in_n_out.times)):
                if self.ts.in_n_out.data[i] == 1 and start == None: 
                    start = self._convert_to_datetime(self.ts.in_n_out.times[i])
                elif self.ts.in_n_out.data[i] == 0 and start != None:
                    ax.axvspan(start, 
                               self._convert_to_datetime(self.ts.in_n_out.times[i-1]),
                               facecolor='g', alpha=0.2) 
                    start = None
    
    def _convert_to_datetime(self, time):
        return datetime.date(int(time[0:4]), int(time[4:6]), int(time[6:8]))


    def _format_x_axis(self, ax):
        datemin = datetime.date(self.times[0].min().year, 1, 1)
        datemax = self.times[0].max()

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_minor_locator(mdates.MonthLocator())
        
        ax.set_xlim(datemin, datemax)
        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        return ax

    def _add_text(self, fig):
        padding = 0.01
        text_size = 'small'
        v_start = 0.8
        v_space = 0.05

        fig.text(0.05,0.9, self.symbol, fontsize='xx-large')


        info = ['Market Cap: ', 
                    'P/E: ', 
                    'EPS: ']

        if (self.ts != None):
            ts_info = ['Enter Signal: ' + str(self.ts.enter_signal),
                       'Exit Signal: ' + str(self.ts.exit_signal),
                       'Trading Commission: $' + str(self.ts.trading_commission),
                       'Performance Index: ' + str(self.ts.performance_index[ 'p_index' ].data[-1]) ]
            for i in ts_info:
                info.append(i)

        for i in range (0, len(info)):
            fig.text(padding, v_start - i*v_space
                     ,info[i], fontsize=text_size)
       
        


if __name__ == '__main__':
    import symbol

    k=symbol.Symbol('GOOG', '20050901', '20090924')

    m=Chart(k)
    m.add_main_plot(k.close)
    m.add_subplot(k.close.rsi('20060905', '20090924', 14))
    #m.add_subplot(k.close.rsi('20060905', '20090924', 6))
    m.show()
