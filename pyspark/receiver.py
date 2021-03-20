#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/11 21:13
# @Author  : MengnanChen
# @Site    : 
# @File    : receiver.py
# @Software: PyCharm Community Edition

'''
receive data coming from kafka (producer.py) and insert data into mongodb
'''
# debug spark—submit by pycharm (Chinese): https://blog.csdn.net/zj1244/article/details/78893837
# (English): https://stackoverflow.com/questions/35560767/pyspark-streaming-with-kafka-in-pycharm
import pymongo
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json
import global_vals
from mongo_utils import mongo_utils

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["sachdeva"]
mycol = mydb["datamart"]

def insert_row(x):
    print(x)
    if x is None or len(x)<1:
        return
    data_list=x.split(',')
    mydict = {
                'domainName': data_list[0],
                'tagName': data_list[1],
                'event': data_list[2],
                'uid': data_list[3]
    }
    #x = mycol.insert_one(mydict)

sc=SparkContext(master='local[*]',appName='test')
ssc=StreamingContext(sc,batchDuration=global_vals.data_produce_duration)
brokers='localhost:9092'
topic=global_vals.kafka_topic
kvs=KafkaUtils.createDirectStream(ssc,[topic],kafkaParams={"metadata.broker.list":brokers})
kvs.pprint()
lines=kvs.map(lambda x:'{},{},{},{}'.format(json.loads(x[1])['timestamp'],json.loads(x[1])['uid'],
                                           json.loads(x[1])['heart_rate'],json.loads(x[1])['steps']))
lines.foreachRDD(lambda rdd:rdd.foreach(insert_row))

ssc.start()
ssc.awaitTermination()