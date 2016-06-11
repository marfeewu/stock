#-*- coding: utf-8 -*-
#standoard package and module load
import urllib.parse
import urllib.request
from lxml import etree
from package.stock import configload
from package.stock import stocklog
from package.stock import dbaction
from datetime import datetime
import socket
from dateutil.relativedelta import relativedelta


#config load
cfg = configload.loadcfg()

#log initial
plog = stocklog.processloginitial(cfg)



def getStockDataByStockNo(stock_no,from_date,to_date):
    last_month = from_date + relativedelta(months=-1)
    tmpstockdata = []
    allstockdata = []
    timeout = 2
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
            print("error:", e.code)
            print("url:", url)
            print(e.read().decode("utf8"))
            #---allen
            if e.code == 404:
                print("url:", url)
                print ("404 error stock_no:", stock_no,"from_data:", from_date,"to_date", to_date)
                plog.info("url: %s" % url)
                plog.info("404 error stock_no: %s from_data: %s to_date: %s" % (stock_no, from_date, to_date))
                return None
            #---

        #---allen
        try:
            html = response.read().decode('big5')
        except UnicodeDecodeError:
            print("url:", url)
            print ("decode error stock_no:", stock_no,"from_data:", from_date,"to_date", to_date)
            plog.info("url: %s" % url)
            plog.info("decode error stock_no: %s from_data: %s to_date: %s" % (stock_no, from_date, to_date))
            return None
        #---

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
    return allstockdata

def main():
    plog.info("----------日誌記錄開始:增加更早日期之上市股票股價----------")
    stockidlist = dbaction.qGetAllStockByCategoryType(1)
    #from_date = datetime.today().replace(day=1)
    #to_date = from_date + relativedelta(years=0-int(cfg['quotedatarange']['duration']))
    for x in stockidlist :
        #---allen
        from_date = dbaction.qGetLastDateDataByStockId_min(x)
        if from_date is None:
            from_date = datetime.today().replace(day=1)
        to_date = from_date + relativedelta(years=0-int(cfg['quotedatarange']['duration']))
        print ("stockidlist", x, "from_date", from_date, "to_date", to_date)
        #bug: 時間會無限延伸
        #plog.info("stockidlist: %s from_data: %s to_date: %s" % (x, from_date, to_date))
        data = getStockDataByStockNo(x,from_date,to_date)
        #data = getStockDataByStockNo(x[0],from_date,to_date)
        if data != None:
        #---
            if len(data) > 0 :
                for i in data :
                    dbaction.insertSimpleDailyQuotes(i)

    plog.info("----------日誌記錄結束:增加更早日期之上市股票股價----------")

if __name__ == '__main__':
    main()




