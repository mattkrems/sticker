#!/usr/bin/env python
# -*- coding: utf-8 mode: python -*-

# util.py - Collection of utilities.
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

import datetime

# -----------------------------------------------------------
def date_range(start_date,end_date):
    date_range = []
    d = start_date
    while d <= end_date:
        date_range.append(d)
        d = d + datetime.timedelta(1)
    return date_range


def convert_to_datetime(time):
        return datetime.date(int(time[0:4]), int(time[4:6]), int(time[6:8]))
