# -*- coding: utf8 -*-
__author__ = 'sai'


class WriterResult:
    # ResultWriter method
    def __init__(self):
        self.rows = []

    # ResultWriter method
    def write_line(self, values, header_class=None):
        self.rows.append({f.system_name: v for f, v in values.items()})


class EnterParamsFake:
    server = "68.183.0.119:27017"
    usermongodb = "anonymous"
    passwordmongodb = "anonymous"


class WriteLog:
    @classmethod
    # LogWriter method
    def info(cls, message, *args):
        pass

    @classmethod
    # LogWriter method
    def error(cls, message, *args):
        pass
