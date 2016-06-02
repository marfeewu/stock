from package.stock import configload
from package.stock import stocklog
from package.stock import dbaction
from datetime import datetime,date
from package.stock import dataparser
import os,sys,traceback,csv

#config load
cfg = configload.loadcfg()

#log initial
plog = stocklog.processloginitial(cfg)




def main():
    plog.info("----------日誌記錄開始:計算上市及大盤分析資料----------")
    stockidlist = dbaction.qGetAllStockByCategoryType(1)
    stockidlist.append(cfg['other']['MarketCode'])
    period_list = str(cfg['other']['Stock_MA_Period']).split(',')
    new_stock_list = []
    timestamp = datetime.now()
    for p in period_list:
        for y in stockidlist:
            new_stock_list.append((y,p))

    #排除已計算過的分析資料
    stockidlist_tmp = []
    ma_result = []
    global error_code
    error_code = 0
    logpath = cfg['path']['logPath']
    analysislogfolder = './' + logpath + '/' + 'analysis/'
    now = date.today()
    filfullename = analysislogfolder + str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2) + '.csv'
    if os.path.exists(filfullename):
        excludelist = []
        tmp_list = []
        csvfile = open(filfullename, 'r')
        for row in csvfile:
            tmp_list = row.split(sep=',')
        for value in tmp_list:
            tmp_value = value.strip('\n').split('/')
            excludelist.append((tmp_value[0],tmp_value[1]))
        stockidlist_tmp[:] = [(x,y) for x,y in new_stock_list if (x,"MA"+str(y)) not in excludelist]
        new_stock_list = stockidlist_tmp

    try:
        for (x,y) in new_stock_list :
            result = dataparser.getMAForStock(x,datetime.today(),timestamp,y)
            if len(result) > 0 :
                dbaction.insertanalysisData(result)
                logpath = cfg['path']['logPath']
                analysislogfolder = './' + logpath + '/' + 'analysis/'
                now = date.today()
                filfullename = analysislogfolder + str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2) + '.csv'

                if not os.path.exists(analysislogfolder):
                    os.makedirs(analysislogfolder)

                if not os.path.exists(filfullename):
                    with open(filfullename, 'w', newline='') as csvfile:
                        w = csv.writer(csvfile, delimiter=',')
                        w.writerow([x + "/" + "MA" + str(y)])
                        csvfile.close()
                else:
                    with open(filfullename, 'r') as csvfile:
                        data = []
                        r = csv.reader(csvfile)
                        for row in r:
                            data = row
                            data.append(x + "/" + "MA" + str(y))
                        csvfile.close()
                    with open(filfullename, 'w', newline='') as csvfile:
                        w = csv.writer(csvfile, delimiter=',')
                        w.writerow(data)
                        csvfile.close()
    except:
        plog.error(sys.exc_info())
        plog.error(traceback.print_exc())
        pass

    plog.info("----------日誌記錄結束:計算上市及大盤分析資料----------")

if __name__ == '__main__':
    main()