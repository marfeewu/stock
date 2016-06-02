#-*- coding: utf-8 -*-

import configparser
from pathlib import Path

def loadcfg():
    cfg = configparser.ConfigParser()
    try:
        pjpath = str(Path(__file__).parent.parent.parent)
        cfgfilepath = pjpath + "/config.ini"
        cfg.read(cfgfilepath)
    except:
        print("configration file is not exist ,please create \'config.ini\' in the root of \'stock \' folder.")

    finally:
        return cfg
