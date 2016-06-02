#-*- coding: utf-8 -*-

#standoard package and module load
import sys
import traceback
import urllib.parse
import urllib.request
from lxml import etree
from package.stock import configload
from package.stock import stocklog
from package.stock import dbaction

#config load
cfg = configload.loadcfg()

#log initial
plog = stocklog.processloginitial(cfg)


def main():
    plog.info("----------日誌記錄開始:所有上市股票代碼----------")
    yahooWebsite = cfg['webpage']['YahooStockWebsite']
    defaulturl = yahooWebsite
    tse = "1"
    category = "上市"
    form = "menu"
    form_id = "stock_id"
    form_name = "stock_name"
    domain = "0"
    stock_cat = []
    stock_cat_tmp = []
    stock_all = []
    error_code = 0

    defaultvalues = {
        'tse': tse,
        'cat': category,
        'form': form,
        'form_id': form_id,
        'form_name': form_name}

    defaultpara = urllib.parse.urlencode(defaultvalues)
    req = urllib.request.Request(defaulturl, defaultpara.encode('big5'))
    response = urllib.request.urlopen(req)
    html = response.read().decode('big5')
    code = html.encode('big5')
    stockdata = etree.HTML(code)


    #所有產業分類
    catstd = stockdata.xpath(u"//table[3]/tr/td/table/tr/td/a")

    for t in catstd :
        stock_cat.append(t.text)

    stock_cat.remove('上櫃')
    stock_cat.remove('存託憑證')
    stock_cat.remove('ETF')
    stock_cat.remove('受益證券')
    stock_cat.remove('其他')
    stock_cat.remove('市認購')
    stock_cat.remove('市認售')
    stock_cat.remove('指數類')
    stock_cat.remove('市牛證')
    stock_cat.remove('市熊證')

#先將上市產業別寫入資料庫
    stock_cat_tmp[:] = [j for j in stock_cat if not dbaction.qStockIndustryType(j)]
    if len(stock_cat_tmp) > 0:
        for y in stock_cat_tmp:
            newid = dbaction.qGetMaxIndustryID()
            record = (y, tse, newid)
            dbaction.insertStockIndustryType(record)



    for idx,stockcat in enumerate(stock_cat) :
        catvalues = {'tse' : tse,
                 'cat' : stockcat,
                 'form' : form,
                 'form_id' : form_id,
                 'form_name' : form_name,
                 'domain' : domain
                     }
        catpara = urllib.parse.urlencode(catvalues)
        catreq = urllib.request.Request(defaulturl, catpara.encode('big5'))
        catresp = urllib.request.urlopen(catreq)
        cathtml = catresp.read().decode('big5', "ignore")
        catcode = cathtml.encode('big5')
        catdata = etree.HTML(catcode)

    #各產業所屬股票
        stocktd = catdata.xpath(u"//form[2]/table/tr/td/table/tr/td/a")
        plog.info(stockcat)
        stock_tmp = []

        for t in stocktd:
            try:
                if t.text is not None:
                    text = t.text.strip()
                    s = text.split(' ')
                    industryid = dbaction.qStockIndustryIdByName(stockcat)
                    tmplist = (s[0], s[1], tse,industryid)
                    stock_tmp.append(tmplist)
                else:
                    print('NoneType')
            except :
                error_code = 1
                plog.error(sys.exc_info())
                plog.error(traceback.print_exc())
                pass

        stock_all.append(stock_tmp)
        plog.info(stock_tmp)

    if error_code == 0:
        for stockmasterrecord in stock_all:
            stock_master_tmp = [h for h in stockmasterrecord if not dbaction.qStockMaster(h)]
            if len(stock_master_tmp) > 0:
                for z in stock_master_tmp:
                        dbaction.inserStockMaster(z)
            stock_master_tmp.clear()
    plog.info("----------日誌記錄結束:所有上市股票代碼----------")

if __name__ == '__main__':
    main()
