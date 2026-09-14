# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyHandler.py
   Description :
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/03:
                   2020/05/26: 区分http和https
-------------------------------------------------
"""
__author__ = 'JHao'

from helper.proxy import Proxy
from db.dbClient import DbClient
from handler.configHandler import ConfigHandler


class ProxyHandler(object):
    """ Proxy CRUD operator"""

    def __init__(self):
        self.conf = ConfigHandler()
        self.db = DbClient(self.conf.dbConn)
        self.db.changeTable(self.conf.tableName)

    def get(self, https=False, protocol=None):
        """
        return a proxy
        Args:
            https: True/False
        Returns:
        """
        proxy = self.db.get(https) if protocol is None else self.db.get(https, protocol=protocol)
        return Proxy.createFromJson(proxy) if proxy else None

    def pop(self, https=False, protocol=None):
        """
        return and delete a useful proxy
        :return:
        """
        proxy = self.db.pop(https) if protocol is None else self.db.pop(https, protocol=protocol)
        if proxy:
            return Proxy.createFromJson(proxy)
        return None

    def put(self, proxy):
        """
        put proxy into use proxy
        :return:
        """
        self.db.put(proxy)

    def delete(self, proxy):
        """
        delete useful proxy
        :param proxy:
        :return:
        """
        return self.db.delete(proxy.storage_key)

    def getAll(self, https=False, protocol=None):
        """
        get all proxy from pool as Proxy list
        :return:
        """
        proxies = self.db.getAll(https) if protocol is None else self.db.getAll(https, protocol=protocol)
        return [Proxy.createFromJson(_) for _ in proxies]

    def exists(self, proxy):
        """
        check proxy exists
        :param proxy:
        :return:
        """
        return self.db.exists(proxy.storage_key)

    def getCount(self):
        """
        return raw_proxy and use_proxy count
        :return:
        """
        total_use_proxy = self.db.getCount()
        return {'count': total_use_proxy}
