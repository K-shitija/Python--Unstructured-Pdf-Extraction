# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 15:23:20 2024

@author: KSHITIJA
"""

import re

import requests
import pdfplumber
import pandas as pd
from collections import namedtuple

Inv = namedtuple('Inv', 'vend_num vend_name inv_dt due_dt inv_amt net_amt description')
def download_file(url):
    local_filename = url.split('/')[-1]
    
    with requests.get(url) as r:
        with open(local_filename, 'wb') as f:
            f.write(r.content)
        
    return local_filename

ap_url = 'https://www.tabs3.com/support/sample/apreports.pdf'
ap = download_file(ap_url)
with pdfplumber.open(ap) as pdf:
    page = pdf.pages[16]
    text = page.extract_text()
print(text)

new_vend_re = re.compile(r'^\d{3} [A-Z].*')
for line in text.split('\n'):
    if new_vend_re.match(line):
        print(line)
        
for line in text.split('\n'):
    if new_vend_re.match(line):
        vend_num , *vend_name = line.split()
        vend_name = ' '.join(vend_name)
        print(vend_num)
        print(vend_name)
                


inv_line_re = re.compile(r'(\d{6}) (\d{6}) ([\d,]+\.\d{2}) [\sP]*([\d,]+\.\d{2}) [YN ]*\d (.*?) [*\s\d]')
line_items = []
for line in text.split('\n'):
    if new_vend_re.match(line):
        vend_num, *vend_name = line.split()
        vend_name = ' '.join(vend_name)    
    
    line = inv_line_re.search(line)
    print(line)
    if line:
        inv_dt = line.group(1)
        due_dt = line.group(2)
        inv_amt = line.group(3)
        net_amt = line.group(4)
        desc = line.group(5)
        line_items.append(Inv(vend_num, vend_name, inv_dt, due_dt, inv_amt, net_amt, desc))
df = pd.DataFrame(line_items)
print(df.head())

df['inv_dt'] = pd.to_datetime(df['inv_dt'])
df['due_dt'] = pd.to_datetime(df['due_dt'])

df['inv_amt'] = df['inv_amt'].map(lambda x: float(x.replace(',', '')))
df['net_amt'] = df['net_amt'].map(lambda x: float(x.replace(',', '')))


writer = pd.ExcelWriter('AP_Reports.xlsx', engine='xlsxwriter')

# write data to the excel sheet
df.to_excel(writer, sheet_name='Reports', index=False)

# close file
writer.close()