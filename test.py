#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 16:57:18 2019

@author: nick_evershed
"""
#%%

import pandas as pd

df = pd.read_csv('combined.csv')

df.sort_values(['period'], inplace=True)

df['difference'] = df[['DiffMedianHourlyPercent','EmployerName']].groupby(['EmployerName'], as_index=False).diff()
