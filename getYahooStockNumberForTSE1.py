#-*- coding: utf-8 -*-

#standoard package and module load
import sys,io,gzip
import traceback
import urllib.parse
import urllib.request
from lxml import etree
from package.stock import configload
from package.stock import stocklog
from package.stock import dbaction

from urllib.error import HTTPError

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
    domain = "0"

    defaultvalues = {
        'tse': tse,
        'cat': category,
        'form': form,
        'form_id': form_id,
        'form_name': form_name}

    defaultpara = urllib.parse.urlencode(defaultvalues)
    req = urllib.request.Request(defaulturl, defaultpara.encode('big5'))
    req.add_header('User-Agent' ,
                   'Mozilla/5.0(Macintosh;Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')
    req.add_header('Accept' , 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    req.add_header('Accept-Charset' , 'ISO-8859-1,utf-8;q=0.7,*;q=0.3')
    req.add_header('Accept-Encoding' , 'gzip, deflate, sdch, br')
    req.add_header('Connection' , 'keep-alive')

    try:
        response = urllib.request.urlopen(req)
    except HTTPError as e:
        content = e.read().decode("utf8", 'ignore')

    if response.info().get('Content-Encoding') == 'gzip':
        buf = io.BytesIO(response.read())
        gzip_f = gzip.GzipFile(fileobj=buf)
        html = gzip_f.read().decode('cp950')
    else:
        html = response.read().decode('cp950')

    code = html.encode('cp950')
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
            record = (y,newid,tse)
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

        catreq.add_header('User-Agent',
                       'Mozilla/5.0(Macintosh;Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')
        catreq.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        catreq.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3')
        catreq.add_header('Accept-Encoding', 'gzip, deflate, sdch, br')
        catreq.add_header('Connection', 'keep-alive')


        catresp = urllib.request.urlopen(catreq)

        if catresp.info().get('Content-Encoding') == 'gzip':
            buf = io.BytesIO(catresp.read())
            gzip_f = gzip.GzipFile(fileobj=buf)
            cathtml = gzip_f.read().decode('cp950')
        else:
            cathtml = catresp.read().decode('cp950')

        catcode = cathtml.encode('cp950')
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
                    tmplist = (s[0], s[1], tse, industryid)
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
