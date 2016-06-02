from package.stock import configload
from package.stock import stocklog
from package.stock import dbaction
import numpy
import talib
from datetime import date
import os,csv


#config load
cfg = configload.loadcfg()

#log initial
plog = stocklog.processloginitial(cfg)


def getMAForStock(stock_id,get_date,timestamp,period,matype=0):
    ma_list = []
    create_date = str(get_date.year-1911) + "/" + str(get_date.month).zfill(2) + "/" + str(get_date.day).zfill(2)
    data = dbaction.qGetPeriodHistoryClosePriceByStockNo(stock_id)
    new_data = []
    ma_result = []
    for x in data:
        if ',' in str(x[1]):
            k = x[1].replace(',', '')
            new_data.append((x[0], k))
        else:
            new_data.append(x)
    np = numpy.array([k[1] for k in new_data], dtype=numpy.float)
    if len(np) > 0:
        ma_result = talib.MA(np, int(period), matype=matype)

    for i, y in enumerate(ma_result):
        if i - (int(period) - 1) < 0:
            continue
        ma_list_tmp = []
        ma_list_tmp.append("MA" + str(period))
        ma_list_tmp.append(stock_id)
        ma_list_tmp.append(create_date)
        ma_list_tmp.append(data[i][0])
        ma_list_tmp.append('%.2f' % round(y, 2))
        ma_list_tmp.append("")  # sigma1 = ""
        ma_list_tmp.append("")  # sigma2 = ""
        ma_list_tmp.append(timestamp)
        ma_list.append(ma_list_tmp)

    return ma_list