# coding: utf-8

# db.getCollection('domainduplicate').find({$where: "this.value.length > 2"})

from systemtools.basics import *
from datatools.jsonreader import *
from datatools.url import *
from datastructuretools.setqueue import *
from machinelearning.function import *
from datatools.csvreader import *
from datastructuretools.hashmap import *
from systemtools.basics import *
try:
    from systemtools.hayj import *
    import selenium
    from selenium import webdriver
    import ipgetter
    from hjwebbrowser.utils import *
    from hjwebbrowser.utils import *
except: pass
from systemtools.duration import *
from systemtools.file import *
from systemtools.logger import log, logInfo, logWarning, logWarning, logError, Logger
from systemtools.location import *
from systemtools.system import *
import random
import re
from threading import Thread, Lock, Semaphore, active_count
import math
import numpy
from queue import *
import html2text
from domainduplicate import config as ddConf
from multiprocessing import Lock

domainDuplicateSingleton = None
domainDuplicateSingletonLock = Lock()
def getDomainDuplicateSingleton(*args, **kwargs):
    global domainDuplicateSingleton
    with domainDuplicateSingletonLock:
        if domainDuplicateSingleton is None:
            domainDuplicateSingleton = DomainDuplicate(*args, **kwargs)
    return domainDuplicateSingleton

class DomainDuplicate:
    """
        See the README for more informations
    """
    def __init__ \
    (
        self,
        limit=10000000,
        user=None, password=None, host=None, # For the mongodb database
        logger=None,
        verbose=True,
        useMongodb=None,
        maxDuplicates=10,
        name="domainduplicate",
        cleanEachNAction=10000,
        doSerialize=True,
    ):
        self.doSerialize = doSerialize
        self.useMongodb = useMongodb
        if self.useMongodb is None:
            self.useMongodb = ddConf.useMongodb
        self.name = name
        self.maxDuplicates = maxDuplicates
        self.logger = logger
        self.verbose = verbose
        if user is None:
            user = ddConf.user
        if password is None:
            password = ddConf.password
        if host is None:
            host = ddConf.host
        if self.useMongodb:
            if user is None and password is None and host is None:
                try:
                    (user, password, host) = getOctodsMongoAuth(logger=self.logger, verbose=self.verbose)
                except Exception as e:
                    logException(e, self, message="You must give user password and host for the mongo database.")
        self.data = SerializableDict\
        (
            name=self.name,
            logger=self.logger,
            verbose=self.verbose,
            limit=limit,
            cacheCheckRatio=0.0,
            useMongodb=self.useMongodb,
            user=user, password=password, host=host,
            cleanEachNAction=cleanEachNAction,
            doSerialize=self.doSerialize,
        )
        self.urlParser = URLParser()

    def hash(self, url, title, html):
        if html is None:
            html = ""
        domain = self.urlParser.getDomain(url)
        text = str(domain) + "_" + str(title) + "_" + html2text.html2text(html)
        return md5(text)

    def setMaxDuplicates(self, maxDuplicates):
        self.maxDuplicates = maxDuplicates

    def isDuplicate(self, url=None, title=None, html=None, addElement=True):
        """
            This function check if the given url, title, html is duplicates over previous title, html of the same domain.
            It will add the current page to the database.
            The number of duplicates is the number of occurence of the element -1. For example if there is 3 same elements in your database, there will be 2 duplicates. So you can set maxDuplicates to 0 to have only one element...
        """
        url = self.urlParser.normalize(url)
        theHash = self.hash(url, title, html)
        duplicateCount = 0
        if self.data.has(theHash):
            allDuplicates = self.data[theHash]
            duplicateCount = len(allDuplicates)
            if addElement:
                self.data[theHash] = list(set(allDuplicates + [url]))
        else:
            if addElement:
                self.data[theHash] = [url]
        return duplicateCount > self.maxDuplicates


# class DomainDuplicateCacheDEPRECATED:
#     """
#         This class use a thread cacheLock itself.
#
#         This class produce struc like this:
#
#         {
#             <domain1>:
#             {
#                 <hash>: (<timestamp>, {<link1>, <link2>}),
#                 2a86a85c540a9cf9b7ce47b9ed7f94f3: (1509021979.7977126, {'http://test2.com/89468541', 'http://test2.com/8949841'}),
#                 b9e031ab7e67ec9c142e63101df705d1: (1509021979.797777, {'http://test2.com/8941'})
#             },
#             test.com:
#             {
#                 c9281a1d6a23f80f980fae619de83f97: (1509021979.797593, {'http://test.com/564651'})
#             }
#         }
#
#         So you can watch if the content of a url is the same content
#         of an other url in the same domain...
#         Sometimes website block ips by sending a html content with a message,
#         so you can easily detect it by watching the similarity over different urls.
#     """
#     def __init__(
#                     self,
#                     maxHashCount=10000,
#                     purgeAndSaveEachAdd=10,
#                     fileId="",
#                     dataDirPath=None,
#                 ):
#         if dataDirPath is None:
#             dataDirPath = tmpDir()
#         self.dataPath = dataDirPath + "/" + type(self).__name__.lower() + fileId + ".pickle"
#         if fileExists(self.dataPath):
#             self.data = deserialize(self.dataPath)
#         else:
#             self.data = {}
#         self.maxHashCount = maxHashCount
#         self.purgeAndSaveEachAdd = purgeAndSaveEachAdd
#         self.urlParser = URLParser()
#         self.addCount = 0
#         self.cacheLock = Lock()
#
#     def hash(self, title, html):
#         if html is None:
#             html = ""
#         text = str(title) + "_" + html2text.html2text(html)
#         return md5(text)
#
#     def isDuplicate(self, url, title, html, maxDuplicatePerDomain):
#         if self.count(url, title, html) > maxDuplicatePerDomain:
#             return True
#         else:
#             return False
#
#     def getTimestamp(self):
#         return time.time()
#
#     def close(self):
#         self.purgeAndSave()
#
#     def purgeAndSave(self):
#         self.purge()
#         self.save()
#
#     def purge(self):
#         with self.cacheLock:
#             # We count the number of urls in data:
#             hashSize = self.hashSize()
#             # Then it's too much:
#             if hashSize > self.maxHashCount:
#                 # We get all:
#                 plateDHT = [] # For Domain Hash Timestamp
#                 for domain, hashs in self.data.items():
#                     for hash, (timestamp, urls) in hashs.items():
#                         plateDHT.append((domain, hash, timestamp))
#                 # We sort all:
#                 plateDHT = sortBy(plateDHT, desc=False, index=2)
#                 # We delete old ones:
#                 toDeleteCount = hashSize - self.maxHashCount
#                 if len(plateDHT) > toDeleteCount:
#                     for i in range(toDeleteCount):
#                         (domain, hash, timestamp) = plateDHT[i]
#                         del self.data[domain][hash]
#                         if len(self.data[domain]) == 0:
#                             del self.data[domain]
#
#     def save(self):
#         with self.cacheLock:
#             serialize(self.data, self.dataPath)
#
#     def add(self, url, title, html):
#         toPurgeAndSave = False
#         with self.cacheLock:
#             if url is not None:
#                 hash = self.hash(title, html)
#                 domain = self.urlParser.getDomain(url)
#                 if domain not in self.data:
#                     self.data[domain] = {}
#                 if hash not in self.data[domain]:
#                     self.data[domain][hash] = (None, set())
#                 urls = self.data[domain][hash][1]
#                 urls.add(url)
#                 theTuple = (self.getTimestamp(), urls)
#                 self.data[domain][hash] = theTuple
#
#                 self.addCount += 1
#
#                 if self.purgeAndSaveEachAdd > 0 and \
#                 self.addCount % self.purgeAndSaveEachAdd == 0:
#                     toPurgeAndSave = True
#         if toPurgeAndSave:
#             self.purgeAndSave()
#
#     def size(self, onHash=False):
#         with self.cacheLock:
#             if onHash:
#                 return self.hashSize()
#             else:
#                 return self.urlSize()
#
#     def hashSize(self):
#         count = 0
#         for domain, hashs in self.data.items():
#             for hash, (timestamp, urls) in hashs.items():
#                 count += 1
#         return count
#
#     def urlSize(self):
#         count = 0
#         for domain, hashs in self.data.items():
#             for hash, (timestamp, urls) in hashs.items():
#                 count += len(urls)
#         return count
#
#     def count(self, url, title, html):
#         with self.cacheLock:
#             hash = self.hash(title, html)
#             domain = self.urlParser.getDomain(url)
#             if domain not in self.data:
#                 return 0
#             if hash not in self.data[domain]:
#                 return 0
#             if self.data[domain][hash] is None:
#                 return 0
#             return len(self.data[domain][hash][1])

if __name__ == '__main__':
    print("")
    fileToStr("")
















