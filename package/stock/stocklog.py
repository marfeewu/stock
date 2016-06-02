#-*- coding: utf-8 -*-

import os
import logging
from datetime import date

def configloginitial(cfg):
    #log initial
    logpath =cfg['path']['logPath']
    logfilename = cfg['logfile']['configlog']
    now = date.today()
    configlogfolder = './' + logpath + '/' + 'config/'
    logfullfilename = configlogfolder +  str(now.year) + '-' + str(now.month) + '-' + str(now.day) + logfilename


    if not os.path.exists(configlogfolder):
        os.makedirs(configlogfolder)
    if os.path.exists(logfilename):
        os.remove(logfilename)

    setup_logger('configlog', logfullfilename, logging.DEBUG)
    configlog = logging.getLogger('configlog')
    return configlog

def dbloginitial(cfg):
#log initial
    logpath = cfg['path']['logPath']
    logfilename = cfg['logfile']['dblog']
    now = date.today()
    dblogfolder = './' + logpath + '/' + 'db/'
    logfullfilename = dblogfolder + str(now.year) + '-' + str(now.month) + '-' + str(now.day)  + logfilename


    if not os.path.exists(dblogfolder):
        os.makedirs(dblogfolder)

    if os.path.exists(logfilename):
        os.remove(logfilename)

    setup_logger('dblog', logfullfilename, logging.DEBUG)
    dblog = logging.getLogger('dblog')
    return dblog

def processloginitial(cfg):
    #log initial
    logpath =cfg['path']['logPath']
    logfilename = cfg['logfile']['processlog']
    now = date.today()
    processlogfolder = './' + logpath + '/' + 'process/'
    logfullfilename = processlogfolder + str(now.year) + '-' + str(now.month) + '-' + str(now.day) + logfilename


    if not os.path.exists(processlogfolder):
        os.makedirs(processlogfolder)

    if os.path.exists(logfilename):
        os.remove(logfilename)

    setup_logger('processlog',logfullfilename,logging.DEBUG)
    processlog = logging.getLogger('processlog')
    return processlog


def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.NullHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)