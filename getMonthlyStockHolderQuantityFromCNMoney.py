#-*- coding: utf-8 -*-

#standoard package and module load
import urllib.parse
import urllib.request
from lxml import etree
import time
from package.stock import configload
from package.stock import stocklog
from package.stock import dbaction

#config load
cfg = configload.loadcfg()

#log initial
plog = stocklog.processloginitial(cfg)



def main():
    plog.info("----------日誌記錄開始:董監持股----------")
    cnmoneyWebsite = cfg['webpage']['CNMoneyWebsite']
    defaulturl = cnmoneyWebsite
    stockidlist = []
    stockholderlist = []
    tmpstockholderlist = []
    stockrecord = tuple()

    stockidlist = dbaction.qGetAllStock()
    newstockidlist = [i for i in stockidlist if not dbaction.qStockHolderListByMonthlyId(i)]


    for i,stockid in enumerate(newstockidlist):
        print(stockid[0])
        stockurl = defaulturl + '/' + str(stockid[0]) + '.htm'
        req = urllib.request.Request(stockurl)
        response = urllib.request.urlopen(req)
        html = response.read().decode('utf-8')
        code = html.encode('utf8')
        stockholderdata = etree.HTML(code)
        #所有產業分類
        catstd = stockholderdata.xpath(u"//div[contains(@class,'tabvl')]/table/tr/td")

        for p , t in enumerate(catstd):
            p+=1
            if p % 7 == 0:
                tmpstockholderlist.append(t.text)
                tmpstockholderlist.append(stockid[0])
                stockholderlist.append(tmpstockholderlist)
                tmpstockholderlist = []

            else:
                tmpstockholderlist.append(t.text)

        if len(stockholderlist) != 0:
            for record in stockholderlist:
                if not dbaction.qStockHolderListByMonthly(record):
                    dbaction.insertStockHolderList(record)
        plog.info("已完成" + str(stockid[0]) + "的資料轉入")
    plog.info("----------日誌記錄結束:董監持股----------")


if __name__ == '__main__':
    main()