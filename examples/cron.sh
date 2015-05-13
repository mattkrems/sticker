#!/bin/bash

# -*- coding: utf-8 mode: shell-script -*-

# cron.sh - Simple cron fragment for sticker
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

# copy this file to $HOME/.sticker/cron.sh and execute
#
#  echo "30 13 * * * $HOME/.sticker/cron.sh > /dev/null 2>&1" | crontab -
#
# in order to run sticker every day at 1:30 pm.
# crontab syntax:
#   m h  dom mon dow   command

datestamp=$(date +"%Y-%m-%d")
log_dir=$HOME/.sticker/cron_logs/$datestamp

# create log directory
[ ! -d $log_dir ] && mkdir -p $log_dir

pushd $log_dir
  sticker -m -q $HOME/.sticker/backtest_daily.ini > $log_dir/sticker.log 2>&1
popd

