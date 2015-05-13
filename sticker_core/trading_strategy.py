#!/usr/bin/env python
# -*- coding: utf-8 mode: python -*-

# trading_strategy.py - Module to evaluate trading strategies.
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
import symbol_list as sl
import symbol
import time_series
import portfolio
import trading_chart
import util
import string
import re
import time
import smtplib
from email.MIMEText import MIMEText
from datetime import timedelta, datetime, date
import datetime


# ---------------------------------------------------------------
class TradingStrategyList():
    # -----------------------------------------------------------
    def __init__(self):
        self.components = []
        for bt_index in sc.input[ ('BacktestConfig', 'run_backtest') ]:
            backtest_section = 'BacktestStrategy_' + bt_index
            # append trading strategy object
            self.components.append(TradingStrategy(
                sc.input[ (backtest_section, 'strategy_label') ],
                sc.input[ (backtest_section, 'enter_signal') ],
                sc.input[ (backtest_section, 'exit_signal') ],
                sc.input[ (backtest_section, 'risk_cap') ],
                sc.input[ (backtest_section, 'starting_cash') ],
                sc.input[ (backtest_section, 'chart_functions') ],
                sc.input[ (backtest_section, 'chart_functions_new') ],
                sc.input[ (backtest_section, 'symbol_blacklist') ],
                sc.input[ (backtest_section, 'trading_symbols') ],
                sc.input[ (backtest_section, 'trading_start') ],
                sc.input[ (backtest_section, 'trading_end') ],
                sc.input[ (backtest_section, 'trading_type') ],
                sc.input[ (backtest_section, 'trading_commission') ],
                sc.input[ (backtest_section, 'always_plot') ]))

    # -----------------------------------------------------------
    def run_backtest(self):
        for my_strategy in self.components:
            my_strategy.run_backtest()

            # should we send notification mails?
            if len(my_strategy.has_enter_signal) > 0 or \
                   len(my_strategy.has_exit_signal)  > 0:

                #localtime = time.strftime('%Y%m%d', time.localtime())
                localtime = datetime.date.today()
                mailserver    = sc.config[ ('STickerConfig', 'mail_server') ]
                name          = sc.config[ ('STickerConfig', 'name') ]
                email_address = sc.config[ ('STickerConfig', 'email') ]

                # create message header and body
                msg_str   = '=======[ BacktestStrategy: ' + my_strategy.strategy_label + ' ]=======\n'
                msg_str  += 'enter_signal    : '  + my_strategy.enter_signal + '\n'
                msg_str  += 'exit_signal     : '  + my_strategy.exit_signal  + '\n'
                msg_str  += 'trading_symbols : '  + my_strategy.trading_symbols_label + '\n'
                msg_str  += '\n'
                msg_str  += 'Todays enter recommendation:\n\n'
                for key in my_strategy.has_enter_signal.keys():
                    msg_str += ' - ' + my_strategy.has_enter_signal[ key ]
                msg_str  += '\n'
                msg_str  += 'Todays exit recommendation:\n\n'
                for key in my_strategy.has_exit_signal.keys():
                    msg_str += ' - ' + my_strategy.has_exit_signal[ key ]
                msg_str  += '\n'

                msg = MIMEText(msg_str)
                msg['Subject']  = '[sticker] recommendation of the day - ' + localtime
                msg['From']     = 'STicker v0.1 <sticker@barin.ucsd.edu>'
                msg['To']       = name + ' <' + email_address + '>'

                print '\n\n'
                print msg.as_string()

                if sc.send_email:
                    print 'Sending e-mail to ' + email_address
                    # establish an SMTP object and connect to mail server
                    s = smtplib.SMTP()
                    s.connect("smtp.ucsd.edu")
                    # send the email: real from, real to, extra headers and content ...
                    s.sendmail("sticker@barin.ucsd.edu", email_address, msg.as_string())
                    s.close()



# ---------------------------------------------------------------
class TradingStrategy():
    # -----------------------------------------------------------
    def __init__(self,
                 strategy_label,
                 enter_signal,
                 exit_signal,
                 risk_cap,
                 starting_cash,
                 chart_functions,
                 chart_functions_new,
                 symbol_blacklist,
                 trading_symbols,
                 trading_start,
                 trading_end,
                 trading_type,
                 trading_commission,
                 always_plot):

        self.strategy_label     = strategy_label
        p = re.compile('(\s\s*)')
        self.enter_signal       = p.sub(' ', enter_signal)
        self.exit_signal        = p.sub(' ', exit_signal)
        self.risk_cap           = p.sub(' ', risk_cap)
        self.starting_cash      = starting_cash
        self.chart_functions    = chart_functions
        self.chart_functions_new = chart_functions_new

        self.trading_start  = util.convert_to_datetime(trading_start)
        self.trading_end    = util.convert_to_datetime(trading_end)
        symbol_start = self.trading_start - datetime.timedelta(100)

        self.trading_symbols    = sl.SymbolList(trading_symbols,
                                                symbol_blacklist,
                                                symbol_start,
                                                self.trading_end)
        self.trading_symbols_label = trading_symbols
        #self.trading_start  = datetime.strptime(trading_start, "%Y%M%d")
        #self.trading_end    = datetime.strptime(trading_end, "%Y%M%d")
        self.trading_type       = trading_type
        self.trading_commission = trading_commission
        self.always_plot        = always_plot

        self.daterange = util.date_range(self.trading_start, self.trading_end)
        print self.daterange

        # Portfolio to manage the trading transactions of the strategy
        self.portfolio = portfolio.Portfolio(self.starting_cash,
                                             self.trading_start,
                                             self.trading_commission)

        # time series used to store when we are in or out of the market
        self.in_n_out = None

        self.trading_days = None

        # dictionary with time series of computed indicators
        # time series to store the performance of the current trading strategy
        self.performance_index = {}
        self.stock_chart = {}
        self.indicators = {}

    # -----------------------------------------------------------
    def run_backtest(self):
        print '\n#################################################'
        print 'Backtest strategy:', self.strategy_label
        print '#################################################'
        print
        print 'enter_signal: ', self.enter_signal
        print 'exit_signal : ',  self.exit_signal
        print 'risk_cap    : ',     self.risk_cap
        print

        # --------------------------------------------------------
        def update_dictionary(dictionary, indicator_name, indicator_value):
            try:
                dictionary[ indicator_name ]
            except:
                dictionary[ indicator_name ] = time_series.TimeSeries(self.trading_days, [])
            dictionary[ indicator_name ].data.append(indicator_value)

        p_index_accum = 0
        p_index_hold_accum = 0

        #localtime = time.strftime('%Y%m%d', time.localtime())
        localtime = datetime.date.today()

        self.p_index = {}

        # dictionary to store all securities that have a signal today
        self.has_enter_signal = {}
        self.has_exit_signal = {}
        self.has_risk_cap_signal = {}

        # --------------------------------------------------------
        for my_security in self.trading_symbols.components.keys():
            # shortcut
            security = self.trading_symbols.components[ my_security ]

            # initialize portfolio for strategy (in backtest mode we only deal with one symbol)
            purchase = 0
            self.portfolio = portfolio.Portfolio(float(self.starting_cash),
                                                 self.trading_start,
                                                 self.trading_commission)
            # initialize portfolio for hold
            self.portfolio_hold = portfolio.Portfolio(float(self.starting_cash),
                                                      self.trading_start,
                                                      self.trading_commission)

            # days when we have data available
            self.trading_days = [d for d in self.daterange if d in security.close.times ]

            # time series used to store when we are in or out of the market
            self.in_n_out = time_series.TimeSeries(self.trading_days, [])

            # start with empty dictionaries for the current symbol "my_security"
            self.performance_index = {}
            self.charts = {}
            self.stock_chart = {}
            self.indicators = {}

            in_market = False
            enter_market = False
            leave_market = False
            security_had_enter_signal = False

            # parse 'chart_functions' input string to find out what we should plot
            chart_sections = string.split(self.chart_functions, ';')
            chart_panels = {}
            chart_panels[ 'stock_chart' ] = string.split(chart_sections[0], ':')
            if len(chart_sections) > 1:
                chart_panels[ 'indicators' ]  = string.split(chart_sections[1], ':')

            # begin: loop over trading days
            for date in self.trading_days:
                # ---------------------------------------------------------
                def rsi(exp_m_avg_len):
                    if len(security.close.data) > exp_m_avg_len:
                        ts = security.close.rsi(date, date, exp_m_avg_len)
                    if len(ts.data) > 0:
                        rsi_value = ts.data[0]
                    else:
                        rsi_value = 100
                    return rsi_value
                # ---------------------------------------------------------
                def mfi(m_avg_len):
                    ts = security.close.mfi(security.high, security.low, security.close,
                                            security.volume, date, date, m_avg_len)
                    return ts.data[0]
                # ---------------------------------------------------------
                def l_b_band(bb_len, num_stdev=2):
                    upper, m_avg, lower = security.close.b_bands(date, date, bb_len, num_stdev)
                    return lower.data[0]
                # ---------------------------------------------------------
                def u_b_band(bb_len, num_stdev=2):
                    upper, m_avg, lower = security.close.b_bands(date, date, bb_len, num_stdev)
                    return upper.data[0]
                # ---------------------------------------------------------
                def c_b_band(bb_len, num_stdev=2):
                    upper, m_avg, lower = security.close.b_bands(date, date, bb_len, num_stdev)
                    return m_avg.data[0]
                # ---------------------------------------------------------
                def fsto_k(periods):
                    low  = security.low.low(date, date, periods)
                    high = security.high.high(date, date, periods)
                    fsto_k = 100
                    if len(low.data) > 0 and len(high.data) > 0:
                        sto = security.close.fsto_k(low, high, date, date, periods)
                        fsto_k = sto.data[0]
                    return fsto_k
                # ---------------------------------------------------------
                def fsto_d(periods, m_avg):
                    dstart = datetime.strptime(date, "%Y%M%d") - timedelta(days=periods)
                    #date_start = dstart.strftime("%Y%m%d")
                    print date_start, date, periods
                    low  = security.low.low(date_start, date, periods)
                    high = security.high.high(date_start, date, periods)
                    fsto_k = security.close.fsto_k(low, high, date_start, date, periods)
                    fsto_d = fsto_k.m_avg(date, date, m_avg)
                    return fsto_d[0]
                # ---------------------------------------------------------
                def close_monotonous_up(symbol_name, range_hist_len):
                    try:
                        my_security = self.trading_symbols.components[ symbol_name ]
                    except:
                        print 'Error: Symbol ', symbol_name, ' is not available'
                    return my_security.close.monotonous_up(date, range_hist_len)
                # ---------------------------------------------------------
                def close_monotonous_down(symbol_name, range_hist_len):
                    try:
                        my_security = self.trading_symbols.components[ symbol_name ]
                    except:
                        print 'Error: Symbol ', symbol_name, ' is not available'
                    return my_security.close.monotonous_down(date, range_hist_len)
                # ---------------------------------------------------------
                def mfi_hist_spread(mfi_periods, hist_len):
                    end_index   = self.trading_days.index(date)
                    start_index = end_index - hist_len
                    if start_index >= 0:
                        mfi_hist = security.close.mfi(security.high,  security.low,
                                                      security.close, security.volume,
                                                      self.trading_days[ start_index ],
                                                      date, mfi_periods)
                        return mfi_hist.historic_spread(date, hist_len)
                # ---------------------------------------------------------
                def close_m_avg_up(my_symbol, m_avg, hist_len):
                    m_avg_symbol = symbol.Symbol(my_symbol, self.trading_days[0], self.trading_days[-1])
                    end_index   = self.trading_days.index(date)
                    start_index = end_index - max([m_avg, hist_len])
                    if start_index >= 0:
                        close_m_avg = m_avg_symbol.close.m_avg(self.trading_days[ start_index ],
                                                               date, m_avg)
                        return close_m_avg.monotonous_up(date, hist_len)

                # ---------------------------------------------------------
                def roc(hist_len):
                    end_index   = self.trading_days.index(date)
                    start_index = end_index - hist_len
                    if start_index >= 0:
                        return security.close.roc(date, hist_len)

                # ---------------------------------------------------------
                def roc_s(my_symbol, hist_len):
                    my_symbol = symbol.Symbol(my_symbol, self.trading_days[0], self.trading_days[-1])
                    end_index   = self.trading_days.index(date)
                    start_index = end_index - hist_len
                    if start_index >= 0:
                        return my_symbol.close.roc(date, hist_len)

                # ---------------------------------------------------------
                def d_m_avg(m_avg_len):
                    ts = security.close.derivative_m_avg(date, date, m_avg_len)
                    return ts.data[0]

                # ---------------------------------------------------------
                def d_m_avg_s(my_symbol, m_avg_len):
                    start_date = datetime.strptime(self.trading_days[0], "%Y%M%d") - timedelta(days=300)
                    mysymbol = symbol.Symbol(my_symbol, start_date, self.trading_days[-1])
                    ts = mysymbol.close.derivative_m_avg(date, date, m_avg_len)
                    return ts.data[0]


                # ---------------------------------------------------------
                open      = security.open.data[security.open.get_index(date)]
                high      = security.high.data[security.high.get_index(date)]
                low       = security.low.data[security.low.get_index(date)]
                close     = security.close.data[security.close.get_index(date)]
                volume    = security.volume.data[security.volume.get_index(date)]

                if sc.verbose:
                    print date, 'open  : ', open
                    print date, 'high  : ', high
                    print date, 'low   : ', low
                    print date, 'close : ', close
                    print date, 'volume: ', volume

                # ---------------------------------------------------------
                # compute market_cap in billions, set mcap to zero if only N/A is given
                market_cap = security.extra[ 'market_cap' ]
                if market_cap[-1] == 'B':
                    mcap = float(market_cap.strip(market_cap[-1]))
                elif market_cap[-1] == 'M':
                    mcap = float(market_cap.strip(market_cap[-1]))/1000.0
                else:
                    mcap = 0

                transaction_date = date
                transaction_price = float(open)


                # ---------------------------------------------------------
                # portfolio with steady hold
                if date == self.trading_days[0]:
                    num_shares_hold = int((float(self.portfolio_hold.cash) -
                                           float(self.trading_commission)) / transaction_price)
                    self.portfolio_hold.add_security(security,
                                                     transaction_price,
                                                     num_shares_hold,
                                                     transaction_date)
                if date == self.trading_days[-1]:
                    self.portfolio_hold.delete_security(security,
                                                        transaction_price,
                                                        num_shares_hold,
                                                        transaction_date)


                # ---------------------------------------------------------
                if enter_market:
                    num_shares = int((float(self.portfolio.cash) -
                                      float(self.trading_commission)) / transaction_price)
                    self.portfolio.add_security(security,
                                                transaction_price,
                                                num_shares,
                                                transaction_date)
                    if sc.verbose:
                        self.portfolio.print_holdings(date)
                    in_market = True
                    enter_market = False
                    purchase = float(open)

                    if sc.verbose:
                        print date, 'transaction_price: ', transaction_price

                # ---------------------------------------------------------
                if in_market and not leave_market: self.in_n_out.data.append(1)
                else:         self.in_n_out.data.append(0)

                # ---------------------------------------------------------
                if leave_market:
                    in_market = False
                    leave_market = False
                    self.portfolio.delete_security(security,
                                                   transaction_price,
                                                   num_shares,
                                                   transaction_date)
                    if sc.verbose:
                        self.portfolio.print_holdings(date)

                    if sc.verbose:
                        print date, 'transaction_price: ', transaction_price


                # ---------------------------------------------------------
                if eval(self.enter_signal):
                    security_had_enter_signal = True
                    if not in_market:
                        enter_market = True
                        if sc.verbose:
                            print '%s - %-4s -' % (date, security.symbol) \
                                  + '------------------------> enter signal'
                    # for query mode store securities that have an enter_signal today
                    if localtime == date:
                        signal_msg  = '%-4s (%-18s) ' % (security.symbol, security.extra['name'])
                        signal_msg += '-  price: ' + security.extra['price']  + \
                                      '  change: ' + security.extra['change'] + \
                                      '  volume: ' + security.extra['volume'] + '\n'
                        self.has_enter_signal[ security.symbol ] = signal_msg

                if eval(self.risk_cap):
                    if in_market:
                        leave_market = True
                        if sc.verbose:
                            print '%s - %-4s -' % (date, security.symbol) \
                                  + '------------------------> risk cap. exiting'
                    # for query mode store securities that have an risk_cap_signal today
                    if localtime == date:
                        signal_msg  = '%-4s (%-18s) ' % (security.symbol, security.extra['name'])
                        signal_msg += '-  price: ' + security.extra['price']  + \
                                      '  change: ' + security.extra['change'] + \
                                      '  volume: ' + security.extra['volume'] + '\n'
                        self.has_risk_cap_signal[ security.symbol ] = signal_msg

                if eval(self.exit_signal):
                    if in_market:
                        leave_market = True
                        if sc.verbose:
                            print '%s - %-4s -' % (date, security.symbol) \
                                  + '------------------------> exit signal'
                    # for query mode store securities that have an exit_signal today
                    if localtime == date:
                        signal_msg  = '%-4s (%-18s) ' % (security.symbol, security.extra['name'])
                        signal_msg += '-  price: ' + security.extra['price']  + \
                                      '  change: ' + security.extra['change'] + \
                                      '  volume: ' + security.extra['volume'] + '\n'
                        self.has_exit_signal[ security.symbol ] = signal_msg


                # compute and store chart functions
                for chart in chart_panels[ 'stock_chart' ]:
                    update_dictionary(self.stock_chart, chart, eval(chart))
                if len(chart_sections) > 1:
                    for chart in chart_panels[ 'indicators' ]:
                        update_dictionary(self.indicators, chart, eval(chart))

                # also store stock_close/stock_open and p_index for all charts
                update_dictionary(self.stock_chart, 'close', close)
                update_dictionary(self.stock_chart, 'open', open)
                performance_index = self.portfolio.evaluate_assets(date) / float(self.starting_cash)
                update_dictionary(self.performance_index, 'p_index', performance_index)

                # new chart_functions syntax
#                chart_sections_new = string.split(self.chart_functions_new, '|')
#                sindex = 0
#                self.plot_panels = {}
#                for section in chart_sections_new:
#                    sindex += 1
#                    chart_plots = string.split(section, '%')
#                    for plot in chart_plots:
#                        plot_s = plot.strip(' ')
#                        plot_function = plot_s[0:-2]
#                        update_dictionary(self.plot_panels, str( (sindex, plot_s) ) , eval(plot_function))
#                update_dictionary(self.plot_panels, str((0,'p_index:b')), performance_index)
#                update_dictionary(self.plot_panels, str((1,'close:b')), close)
#                update_dictionary(self.plot_panels, str((1,'open:b')),  open)

                if sc.verbose:
                    print date, 'performance index:', \
                          self.performance_index[ 'p_index' ].data[-1]
                    print date, \
                          'enter_market:', enter_market, \
                          'leave_market:', leave_market, \
                          'in_market:',     in_market

            # end: loop over trading days
            p_index_data = self.performance_index[ 'p_index' ].data[-1]
            p_index = "%5.3f" % p_index_data
            p_index_accum += p_index_data
            p_index_hold_data = self.portfolio_hold.evaluate_assets(self.trading_days[-1]) / float(self.starting_cash)
            p_index_hold = "%5.3f" % p_index_hold_data
            p_index_hold_accum += p_index_hold_data


            # ---------------------------------------------------------
            if self.portfolio.transactions > 0:
                days_in_market = reduce(lambda x, y: x + y, self.in_n_out.data)
                trading_days   = len(self.trading_days)
                tp_index = "%6.3f" % (trading_days / days_in_market * (p_index_data - 1.0) )
                print '%-7s - performance indices: %s / %s / %s - transactions: %s' \
                      % (security.symbol, p_index, p_index_hold, tp_index, self.portfolio.transactions)
                self.p_index[ security.symbol ] = [self.portfolio.transactions, p_index, p_index_hold, tp_index ]

            if (security_had_enter_signal or self.always_plot):
                sym_chart = trading_chart.TradingChart(security, self)
                filename = security.symbol.ljust(4,'_') + '.' \
                           + self.strategy_label + '_' + str(p_index) + '.png'
                sym_chart.savefig(filename)

        # accumulated performance index
        # ---------------------------------------------------------
        print 'accumulated performance index: ', \
              p_index_accum/len(self.trading_symbols.components.keys()), ' / ', \
              p_index_hold_accum/len(self.trading_symbols.components.keys())

        print '\n---------------------[ Top 20 ]---------------------'
        items = self.p_index.items()
        #items.sort(key=lambda x: x[1][0], reverse=True)
        items.sort(key=lambda x: x[1], reverse=True)
        rank = 0
        print 'symbol    transactions strategy hold    normalized'
        for key, value in items:
            rank += 1
            if rank <= 20:
                print '%-7s :      %3s      %s   %s  %s' % (key, value[0], value[1], value[2], value[3])


