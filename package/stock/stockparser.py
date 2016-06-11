#-*- coding: utf-8 -*-
#standoard package and module load
import os
import urllib.parse
import urllib.request
import urllib.error
import requests
from lxml import etree
from package.stock import configload
from package.stock import stocklog
import socket
from dateutil.relativedelta import relativedelta
from datetime import date,datetime
import csv
import random
import io
import base64

#config load
cfg = configload.loadcfg()

#log initial
plog = stocklog.processloginitial(cfg)


def dailyquotesparserlocal(file):
    stockdate = str(file[4:12])
    # stockdate = stockdate[0:4] + '-' + stockdate[4:6] + '-' + stockdate[6:]
    content = open(file)
    html = content.read()
    data = etree.HTML(html)
    td = data.xpath(u"//table[2]/tbody/tr/td")
    i = 1
    result = []
    subresult = []
    for t in td:
        if t.text is None:
            ft = t.xpath(u"font")
            if len(ft) > 0:
                subresult.append(ft[0].text)
            else:
                print(ft)
        else:
            if i % 16 in (3,4,5,13,15) :
                value = str(t.text).replace(',','')
                subresult.append(int(value))
            elif i % 16 in (0,5,6,7,8,9,11,12,14):
                if t.text == '--':
                    value = 0.0
                else:
                    value = str(t.text).replace(',','')
                    value = float(value)
                subresult.append(value)
            else:
                value = t.text
                subresult.append(value.strip())
        if i % 16 == 0:
            subresult.insert(0, stockdate)
            result.append(subresult)
            subresult = []
        i += 1
    content.close()
    return result

def dailyquotesparserlocaltocsv(file):
    stockdate = str(file[4:12])
    # stockdate = stockdate[0:4] + '-' + stockdate[4:6] + '-' + stockdate[6:]
    content = open(file)
    html = content.read()
    data = etree.HTML(html)
    td = data.xpath(u"//table[2]/tbody/tr/td")

def getStockHTMLDataByStockNo(stock_no,from_date,to_date):
    last_month = from_date + relativedelta(months=-1)
    tmpstockdata = []
    allstockdata = []
    notfound = False
    count = int(cfg['quotedatarange']['duration']) * 12 - 1
    timeout = 5
    socket.setdefaulttimeout(timeout)

    while to_date < last_month:
        url = cfg['webpage']['TWSEWebsite'] + ('ch/trading/exchange/STOCK_DAY/genpage/' +
                'Report%(year)d%(mon)02d/%(year)d%(mon)02d_F3_1_8_%(stock)s.php' +
                '?STK_NO = %(stock)s & myear = %(year)d & mmon = %(mon)02d') % {
                  'year': last_month.year,
                  'mon':  last_month.month,
                  'stock': stock_no}
        req = urllib.request.Request(url)
        try:
            response = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            print(e.code)
            print(e.read().decode("utf8"))
            if e.code == 404:
                count = 0
                notfound = True
                pass
        if not notfound:
            html = response.read().decode('utf-8')
            code = html.encode('big5')
            htmldata = etree.HTML(code)
            stockdata= htmldata.xpath(u"//table[contains(@class,'board_trad')]/tr[contains(@bgcolor,'#FFFFFF')]/td")
            datedata = htmldata.xpath(u"//table[contains(@class,'board_trad')]/tr[contains(@bgcolor,'#FFFFFF')]/td[1]/div")
            p = 0
            for i,t in enumerate(stockdata):
                i+=1
                if i % 9 == 1:
                    tmpstockdata.append(datedata[p].text)
                    tmpstockdata.append(stock_no)
                    p+=1
                elif i % 9 in (2,3,4,5,6,7) :
                    tmpstockdata.append(t.text)
                elif i % 9 == 0 :
                    allstockdata.append(tmpstockdata)
                    tmpstockdata = []
            last_month = last_month + relativedelta(months=-1)
            count -= 1
        else:
            break
    if count == 0:
        logpath = cfg['path']['logPath']
        updatelogfolder = './' + logpath + '/' + 'update/'
        now = date.today()
        filfullename = updatelogfolder + str(now.year) + str(now.month).zfill(2) + '-Market.csv'

        if not os.path.exists(updatelogfolder):
            os.makedirs(updatelogfolder)

        if not os.path.exists(filfullename):
            with open(filfullename, 'w') as csvfile:
                w = csv.writer(csvfile, delimiter=',')
                w.writerow([stock_no])
                csvfile.close()
        else :
            with open(filfullename,'r') as csvfile:
                data = []
                r = csv.reader(csvfile)
                for row in r :
                    data = row
                    data.append(stock_no)
                csvfile.close()
            with open(filfullename,'w') as csvfile:
                w = csv.writer(csvfile, delimiter=',')
                w.writerow(data)
                csvfile.close()
    return allstockdata

def getStockCSVDataByStockNo(stock_no,from_date,to_date):
    last_month = from_date + relativedelta(months=-1)
    allstockdata = []
    notfound = False
    count = int(cfg['quotedatarange']['duration']) * 12 - 1
    timeout = 5
    socket.setdefaulttimeout(timeout)

    while to_date < last_month:

        url = cfg['webpage']['TWSEWebsite'] + ('ch/trading/exchange/STOCK_DAY/STOCK_DAY_print.php?genpage=genpage/' +
                'Report%(year)d%(mon)02d/%(year)d%(mon)02d_F3_1_8_%(stock)s.php' +
                '&type=csv&r=%(rand)s') % {
                  'year': last_month.year,
                  'mon':  last_month.month,
                  'stock': stock_no,
                  'rand' : random.randrange(1, 1000000)}
        req = urllib.request.Request(url)
        try:
            response = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            print(e.code)
            print(e.read().decode("utf8"))
            if e.code == 404:
                count = 0
                notfound = True
                pass
        if not notfound:
            r = csv.reader(io.StringIO(response.read().decode('big5','ignore')))
            tmpstockdata = []
            for i,x in enumerate(r) :
                if i >1:
                #刪除最後兩個欄位
                    del x[-1]
                    del x[-1]
                    x[1] = x[1].replace(',','')
                    x[2] = x[2].replace(',','')
                    x[3] = x[3].replace(',', '')
                    x[4] = x[4].replace(',', '')
                    x[5] = x[5].replace(',', '')
                    x[6] = x[6].replace(',', '')
                    if x[2] == '--':
                        x[2] = 0.0
                    if x[3] == '--':
                        x[3] = 0.0
                    if x[4] == '--':
                        x[4] = 0.0
                    if x[5] == '--':
                        x[5] = 0.0
                    if x[6] == '--':
                        x[6] = 0.0
                    x[0] = x[0].strip()
                    x.insert(1,stock_no)
                    allstockdata.append(x)
            count -= 1
            last_month = last_month + relativedelta(months=-1)
        else:
            break
    if count == 0:
        logpath = cfg['path']['logPath']
        updatelogfolder = './' + logpath + '/' + 'update/'
        now = date.today()
        filfullename = updatelogfolder + str(now.year) + str(now.month).zfill(2) + '.csv'

        if not os.path.exists(updatelogfolder):
            os.makedirs(updatelogfolder)

        if not os.path.exists(filfullename):
            with open(filfullename, 'w') as csvfile:
                w = csv.writer(csvfile, delimiter=',')
                w.writerow([stock_no])
                csvfile.close()
        else :
            with open(filfullename,'r') as csvfile:
                data = []
                r = csv.reader(csvfile)
                for row in r :
                    data = row
                    data.append(stock_no)
                csvfile.close()
            with open(filfullename,'w') as csvfile:
                w = csv.writer(csvfile, delimiter=',')
                w.writerow(data)
                csvfile.close()
    return allstockdata

def getMarketCSVDataByStockNo(stock_no,from_date,to_date):
    last_month = from_date + relativedelta(months=-1)
    allstockdata = []
    notfound = False
    count = int(cfg['quotedatarange']['duration']) * 12 - 1
    timeout = 5
    socket.setdefaulttimeout(timeout)

    while to_date < last_month:
#       日期、總成交金額、總成交數量
        url1 = cfg['webpage']['TWSEWebsite'] + cfg['webpage']['HistoryData']+\
              ('FMTQIK/FMTQIK2.php?STK_NO=&myear=%(year)s&mmon=%(mon)02d' +
                '&type=csv&r=%(rand)s') % {
                  'year': last_month.year,
                  'mon':  last_month.month,
                  'stock': stock_no,
                  'rand' : random.randrange(1, 1000000)}
        req1 = urllib.request.Request(url1)
#       開盤價、收盤價、最高價、最低價
        url_main = cfg['webpage']['TWSEWebsite'] + 'ch/trading/indices/MI_5MINS_HIST/MI_5MINS_HIST.php'
        url_csv = cfg['webpage']['TWSEWebsite'] + 'ch/trading/indices/MI_5MINS_HIST/MI_5MINS_HIST_print.php?language=ch&save=csv'
        main_post_data = urllib.parse.urlencode({'myear':last_month.year-1911,'mmon':str(last_month.month).zfill(2)}).encode()
        req_main = urllib.request.Request(url_main)
        req_csv = urllib.request.Request(url_csv)
        try:
            response1 = urllib.request.urlopen(req1)
            response_main = urllib.request.urlopen(req_main,data=main_post_data)
            html = response_main.read().decode('big5', 'ignore')
            code = html.encode('big5')
            htmldata = etree.HTML(code)
            input_html_data = htmldata.xpath(u"//input[@id='html']/@value")
            b64_html_data = base64.b64encode(str(input_html_data[0]).encode())
            input_dirname_data = htmldata.xpath(u"//input[@id='dirname']/@value")
            b64_dirname_data = base64.b64encode(str(input_dirname_data[0]).encode())
            input_dic = {'html':b64_html_data,'dirname':b64_dirname_data}
#            print(inputdata[0])
            csv_post_data = urllib.parse.urlencode(input_dic).encode()
#            print(csv_post_data)
            response_csv = urllib.request.urlopen(req_csv, data=csv_post_data)
        except urllib.error.HTTPError as e:
            print(e.code)
            print(e.read().decode("utf8"))
            if e.code == 404:
                count = 0
                notfound = True
                pass
        if not notfound:
            r1 = csv.reader(io.StringIO(response1.read().decode('big5','ignore')))
            r2 = csv.reader(io.StringIO(response_csv.read().decode('big5','ignore')))
            data = list(r1)
            data2 = list(r2)
            print(data2)
#           處理日期、總成交金額、總成交數量,del data[0] 2次來刪掉陣列的第一筆和第二筆
            del data[0]
            del data[0]
            del data[-1]
            for i,x in enumerate(data) :
                x[1] = x[1].replace(',','')
                x[2] = x[2].replace(',','')
                x[0] = x[0].strip()
#           del x[3] 3次來刪掉陣列的第三、第四和第五個資料
                del x[3]
                del x[3]
                del x[3]
                x.insert(1,stock_no)
#           處理開盤價、收盤價、最高價、最低價,del data[0] 3次來刪掉陣列的第一筆、第二筆及第三筆
            del data2[0]
            del data2[0]
            del data2[0]
            del data2[-1]
            for j,y in enumerate(data2):
                y[1] = y[1].replace(',','')
                y[2] = y[2].replace(',', '')
                y[3] = y[3].replace(',', '')
                y[4] = y[4].replace(',', '')
                del y[0]
            if len(data) == len(data2):
                for l_data in zip(data,data2):
                    tmp_data = l_data[0] + l_data[1]
                    allstockdata.append(tmp_data)
                count -= 1
                last_month = last_month + relativedelta(months=-1)

            else:
                break
        else:
            break
    if count == 0:
        logpath = cfg['path']['logPath']
        updatelogfolder = './' + logpath + '/' + 'update/'
        now = date.today()
        filfullename = updatelogfolder + str(now.year) + str(now.month).zfill(2) + '.csv'

        if not os.path.exists(updatelogfolder):
            os.makedirs(updatelogfolder)

        if not os.path.exists(filfullename):
            with open(filfullename, 'w') as csvfile:
                w = csv.writer(csvfile, delimiter=',')
                w.writerow([stock_no])
                csvfile.close()
        else :
            with open(filfullename,'r') as csvfile:
                data = []
                r = csv.reader(csvfile)
                for row in r :
                    data = row
                    data.append(stock_no)
                csvfile.close()
            with open(filfullename,'w') as csvfile:
                w = csv.writer(csvfile, delimiter=',')
                w.writerow(data)
                csvfile.close()
    return allstockdata


def getLastestStockHTMLDataByStockNo(stock_no,from_date,to_date):
    next_date = to_date + relativedelta(days=1)
    tmpstockdata = []
    allstockdata = []
    allstockdata_tmp = []
    count = to_date - from_date
    timeout = 5
    socket.setdefaulttimeout(timeout)

    while from_date >= next_date:
        url = cfg['webpage']['TWSEWebsite'] + ('ch/trading/exchange/STOCK_DAY/genpage/' +
                'Report%(year)d%(mon)02d/%(year)d%(mon)02d_F3_1_8_%(stock)s.php' +
                '?STK_NO = %(stock)s & myear = %(year)d & mmon = %(mon)02d') % {
                  'year': next_date.year,
                  'mon':  next_date.month,
                  'stock': stock_no}
        req = urllib.request.Request(url)
        try:
            response = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            print(e.code)
            print(e.read().decode("utf8"))
        html = response.read().decode('big5')
        code = html.encode('big5')
        htmldata = etree.HTML(code)
        stockdata= htmldata.xpath(u"//table[contains(@class,'board_trad')]/tr[contains(@bgcolor,'#FFFFFF')]/td")
        datedata = htmldata.xpath(u"//table[contains(@class,'board_trad')]/tr[contains(@bgcolor,'#FFFFFF')]/td[1]/div")
        p = 0
        for i,t in enumerate(stockdata):
            i+=1
            if i % 9 == 1:
                tmpstockdata.append(datedata[p].text)
                tmpstockdata.append(stock_no)
                p+=1
            elif i % 9 in (2,3,4,5,6,7) :
                tmpstockdata.append(t.text)
            elif i % 9 == 0 :
                allstockdata.append(tmpstockdata)
                tmpstockdata = []
        q = 0
        for x in allstockdata:
            lastdate_tmp = x[0][0].split(sep='/')
            lastdate_str = str(int(lastdate_tmp[0]) + 1911) + str(lastdate_tmp[1]) + str(lastdate_tmp[2])
            lastdate = datetime.datetime.strptime(lastdate_str, '%Y%m%d').date()
            if lastdate > next_date :
                allstockdata_tmp.append(x)
                q += 1
            elif next_date.month == from_date.month:
                if next_date > lastdate:
                   allstockdata_tmp.append(x)
                   q += 1
        next_date += relativedelta(day=q)
        if next_date <= from_date:
            if next_date.month == from_date.month :
                next_date = from_date

        count -= 1
    if count == 0:
        logpath = cfg['path']['logPath']
        updatelogfolder = './' + logpath + '/' + 'update/'
        now = date.today()
        filfullename = updatelogfolder + str(now.year) + str(now.month).zfill(2) + '.csv'

        if not os.path.exists(updatelogfolder):
            os.makedirs(updatelogfolder)

        if not os.path.exists(filfullename):
            with open(filfullename, 'w') as csvfile:
                w = csv.writer(csvfile, delimiter=',')
                w.writerow([stock_no])
                csvfile.close()
        else :
            with open(filfullename,'r') as csvfile:
                data = []
                r = csv.reader(csvfile)
                for row in r :
                    data = row
                    data.append(stock_no)
                csvfile.close()
            with open(filfullename,'w') as csvfile:
                w = csv.writer(csvfile, delimiter=',')
                w.writerow(data)
                csvfile.close()
    return allstockdata

def getLastestStockCSVDataByStockNo(stock_no,from_date,to_date):
    next_date = to_date + relativedelta(days=1)
    allstockdata = []
    allstockdata_tmp = []
    notfound = False
    from_date = from_date.date()
    count = abs((next_date.month - from_date.month))+1
    timeout = 5
    socket.setdefaulttimeout(timeout)

    while from_date.month >= next_date.month:
        url = cfg['webpage']['TWSEWebsite'] + ('ch/trading/exchange/STOCK_DAY/STOCK_DAY_print.php?genpage=genpage/' +
                                               'Report%(year)d%(mon)02d/%(year)d%(mon)02d_F3_1_8_%(stock)s.php' +
                                               '&type=csv&r=%(rand)s') % {
                                                  'year': next_date.year,
                                                  'mon': next_date.month,
                                                  'stock': stock_no,
                                                  'rand': random.randrange(1, 1000000)}
        req = urllib.request.Request(url)
        try:
            response = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            print(e.code)
            print(e.read().decode("utf8"))
            if e.code == 404:
                notfound = True
                count = 0
                pass
        if not notfound:
            r = csv.reader(io.StringIO(response.read().decode('big5', 'ignore')))
            for i, x in enumerate(r):
                if i > 1:
                    # 刪除最後兩個欄位
                    del x[-1]
                    del x[-1]
                    x[1] = x[1].replace(',','')
                    x[2] = x[2].replace(',','')
                    x[3] = x[3].replace(',', '')
                    x[4] = x[4].replace(',', '')
                    x[5] = x[5].replace(',', '')
                    x[6] = x[6].replace(',', '')
                    if x[2] == '--':
                        x[2] = 0.0
                    if x[3] == '--':
                        x[3] = 0.0
                    if x[4] == '--':
                        x[4] = 0.0
                    if x[5] == '--':
                        x[5] = 0.0
                    if x[6] == '--':
                        x[6] = 0.0
                    x[0] = x[0].strip()
                    x.insert(1, stock_no)
                    allstockdata.append(x)
            count -= 1
            next_date = next_date + relativedelta(months=1)
        else:
            break
    if count == 0:
        logpath = cfg['path']['logPath']
        updatelogfolder = './' + logpath + '/' + 'update/'
        now = date.today()
        filfullename = updatelogfolder + str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2) + '.csv'

        if not os.path.exists(updatelogfolder):
            os.makedirs(updatelogfolder)

        if not os.path.exists(filfullename):
            with open(filfullename, 'w') as csvfile:
                w = csv.writer(csvfile, delimiter=',')
                w.writerow([stock_no])
                csvfile.close()
        else :
            with open(filfullename,'r') as csvfile:
                data = []
                r = csv.reader(csvfile)
                for row in r :
                    data = row
                    data.append(stock_no)
                csvfile.close()
            with open(filfullename,'w') as csvfile:
                w = csv.writer(csvfile, delimiter=',')
                w.writerow(data)
                csvfile.close()

    return allstockdata
