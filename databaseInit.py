#-*- coding: utf-8 -*-

import sys,traceback
from package.stock import configload
from package.stock import stocklog
from package.stock import dbaction


#config load
cfg = configload.loadcfg()

#log initial
plog = stocklog.processloginitial(cfg)

def main():

    try :
        dbaction.createTable_stockCategoryType()
        cat_type = [('上市',1),('上櫃',2),('興櫃',3)]

        for x in cat_type:
            if not dbaction.qStockCategoryType(x):
                dbaction.insertStockCategoryType(x)

        dbaction.createTable_stockIndustryType()
        dbaction.createTable_stockMaster()
        dbaction.createTable_simpledailyquotes()
        dbaction.createTable_analysisdata()
    except:
        plog.error(sys.exc_info())
        plog.error(traceback.print_exc())



if __name__ == '__main__':
    main()