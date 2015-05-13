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

import matplotlib
matplotlib.use('Agg')

import pylab
import datetime
import matplotlib.dates as mdates
import sticker_core as sc

# ---------------------------------------------------------------
class TradingChart:
    # -----------------------------------------------------------
    def __init__(self, symbol, trading_strategy):
        self.symbol = symbol
        self.ts = trading_strategy

        self.num_indicators = len(trading_strategy.indicators.keys())
        #self.times = []
        #for t in self.ts.stock_chart['close'].times:
        #    self.times.append(self._convert_to_datetime(t))
        self.times = self.ts.stock_chart['close'].times

    # -----------------------------------------------------------
    def show(self):
        self._make_figure()
        pylab.show()

    # -----------------------------------------------------------
    def savefig(self, filename):
        self._make_figure()
        pylab.savefig(filename,
                      dpi=int(sc.config[ ('STickerConfig', 'dpi') ]),
                      format='png')
        #              format='pdf')
    # -----------------------------------------------------------
    def _make_figure(self):
        #------------------DO NOT TOUCH THIS BLOCK------------
        w = 12.0
        h = 7.0
        aspect = h/w
        h_step = 1

        fig = pylab.figure(figsize=(w,h+self.num_indicators*h_step))

        #must have reasonable starting proportions for main plot and starting
        #  proportion for sub_plot
        srect = [0.20, 0.08, 0.78, 0.87]
        sp_size = 0.14

        main_rect = [srect[0],
                     srect[1]/((h+(self.num_indicators+1)*h_step)/h) + (self.num_indicators+1)*(h_step/(h+h_step*(self.num_indicators+1))),
                     srect[2],
                     srect[3]/((h+(self.num_indicators+1)*h_step)/h)]

        sub_rect = []
        for i in range(1, self.num_indicators+2):
            if i <= self.num_indicators:
                sub_rect.append([srect[0],
                                 main_rect[1] - i*(h_step/(h+h_step*(self.num_indicators+1))),
                                 srect[2],
                                 sp_size/((h+(self.num_indicators+1)*h_step)/h)])
            else:
                pi_rect = [srect[0],
                           main_rect[1] - i*(h_step/(h+h_step*(self.num_indicators+1))),
                           srect[2],
                           sp_size/((h+(self.num_indicators+1)*h_step)/h)]
        #-----------------------------------------------------

        #add figure elements
        self._make_stock_chart(fig, main_rect)
        if self.num_indicators > 0:
            self._make_sub_plot(fig, sub_rect)
        self._make_pi(fig, pi_rect)

        self._add_text(fig)

    # -----------------------------------------------------------
    def _make_stock_chart(self, fig, rect):
        ax = fig.add_axes(rect)

        for key in self.ts.stock_chart.keys():
            ax.plot(self.times,
                    self.ts.stock_chart[key].data,
                    lw = 0.6,
                    label=key)
            
        #make legend
        leg = ax.legend(self.ts.stock_chart.keys(), loc=2)
        for t in leg.get_texts():
            t.set_fontsize('xx-small')

        #turn off x tick labels
        for label in ax.get_xticklabels():
            label.set_visible(False)

        #don't show bottom y tick
        label = ax.get_yticklabels()
        label[0].set_visible(False)

        #formatting options
        self._format_x_axis(ax)
        def price(x): return '$%1.2f'%x
        ax.format_ydata = price
        ax.grid(True)
        self._add_in_n_out(ax)

    # -----------------------------------------------------------
    def _make_sub_plot(self, fig, rect_list):
        ax_list = []
        for rect in rect_list:
            ax_list.append(fig.add_axes(rect))

        ax = 0
        for key in self.ts.indicators.keys():
            ax_list[ax].plot(self.times,
                            self.ts.indicators[key].data,
                            lw=0.6,
                            label=key)

            #make legend
            leg = ax_list[ax].legend([key], loc=2)
            for t in leg.get_texts():
                t.set_fontsize('xx-small')

            #turn off x tick labels
            for label in ax_list[ax].get_xticklabels():
                label.set_visible(False)

            #don't show bottom y tick
            label = ax_list[ax].get_yticklabels()
            label[0].set_visible(False)

            ax = ax+1    

        
        #formatting options
        for ax in ax_list:
            self._format_x_axis(ax)
            self._format_y_ticks(ax)
            ax.grid(True)
            self._add_in_n_out(ax)

    # -----------------------------------------------------------
    def _make_pi(self, fig, rect):
        ax = fig.add_axes(rect)

        for key in self.ts.performance_index.keys():
            ax.plot(self.times,
                    self.ts.performance_index[key].data,
                    lw = 0.6)

        # make legend
        leg = ax.legend(self.ts.performance_index.keys(), loc=2)
        for t in leg.get_texts():
            t.set_fontsize('xx-small')

        # rotate date labels
        ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha='right')

        #formatting options
        self._format_x_axis(ax)
        self._format_y_ticks(ax)
        ax.grid(True)

        self._add_in_n_out(ax)

    # -----------------------------------------------------------
    def _add_in_n_out(self, ax):
        start = None
        for i in range(0, len(self.times)):
            if self.ts.in_n_out.data[i] == 1 and start == None:
                start = self.times[i]
                start_price = self.ts.stock_chart['open'].data[i]
            elif (self.ts.in_n_out.data[i] == 0 and start != None) or (i == len(self.times) - 1 and start != None):
                end_price = self.ts.stock_chart['open'].data[i]
                if end_price > start_price:
                    color = 'g'
                else:
                    color = 'r'
                ax.axvspan(start,
                           self.times[i],
                           facecolor=color,
                           alpha=0.1)
                start = None

    # -----------------------------------------------------------
    def _format_y_ticks(self, ax):
        #half the number of ticks shown
        temp = ax.get_yticks()
        ticks = []
        for i in range(0,len(temp)):
            if i%2 == 0:
                ticks.append(temp[i])
        ax.set_yticks(ticks)

        for label in ax.get_yticklabels():
            label.set_fontsize(9)


    # -----------------------------------------------------------
    def _convert_to_datetime(self, time):
        return datetime.date(int(time[0:4]), int(time[4:6]), int(time[6:8]))


    # -----------------------------------------------------------
    def _format_x_axis(self, ax):
        ax.set_xlim(self.times[0], self.times[-1])
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_minor_locator(mdates.MonthLocator())

        if len(self.times) >= 300:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter(''))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter(''))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter('%b'))

        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        return ax

    # -----------------------------------------------------------
    def _add_text(self, fig):
        padding = 0.01
        text_size = 'x-small'
        v_start = 0.8
        v_space = 0.05
        
        fig.text(0.02,0.9,self.symbol.symbol,fontsize='xx-large')
        fig.text(0.02, 0.87, self.symbol.extra['name'], fontsize='large')

        info = ['Market Cap: ' + self.symbol.extra['market_cap'],
                'P/E: ' + self.symbol.extra['price_earnings_ratio'],
                'EPS: ' + self.symbol.extra['earnings_per_share'],
                'Enter Signal: ' + str(self.ts.enter_signal),
                'Exit Signal: ' + str(self.ts.exit_signal),
                'Risk Cap: ' + str(self.ts.risk_cap),
                'Trading Commission: $' + str(self.ts.trading_commission),
                'Trading Start: ' + str(self.times[0]),
                'Trading End: ' + str(self.times[-1]),
                'Performance Index: ' + str(self.ts.performance_index[ 'p_index' ].data[-1]) ]

        for i in range (0, len(info)):
            fig.text(padding, v_start - i*v_space
                     ,info[i], fontsize=text_size)
