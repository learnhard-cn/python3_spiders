#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月30日 星期四 23时11分10秒
# Brief:
################################################################################
from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo import UpdateOne
import json


# MongoDB config
default_config = {
    "host": "localhost:27017",
    "db": "mydb",
    "user": 'myTestUser',
    "pwd": 'abcd1234',
    "coll": "my_coll"
}


class MongoDb():
    '''
    数据库操作管理模块
    '''
    def __init__(self, host, db, user, pwd, coll):
        '''
        初始化Mongo数据库连接信息
        '''
        self.mongo_host = host
        self.mongo_db = db
        self.mongo_user = user
        self.mongo_pass = pwd
        self.mongo_coll = coll

        try:
            self.uri = 'mongodb://{}:{}@{}/{}'.format(self.mongo_user, self.mongo_pass, self.mongo_host, self.mongo_db)
            self.client = MongoClient(self.uri)
            self.db = self.client[self.mongo_db]
            self.doc = self.db[self.mongo_coll]
        except Exception as e:
            print(e)

    def load_json_filter_dict(self, filter_dict_name):
        '''
        导入JSON文件数据到数据库中
        '''
        with open(filter_dict_name, "r") as f:
            lines = f.readlines()
            data_list = []
            for line in lines:
                data_list.append(json.loads(line))
            self.upsert(data_list)

    def change_db(self, new_db):
        self.db = self.client[new_db]
        self.doc = None

    def list_collections(self):
        print(self.db.list_collection_names())

    def change_collection(self, coll):
        if coll is None:
            return "Invalid collection name, use default:" + self.mongo_db
        print("change collection to [" + coll + "]")
        self.doc = self.db[coll]

    def find_one(self, filter_dict={}):
        print(self.doc.find_one(filter_dict))

    def find_by_objectid(self, obj_id):
        print(self.doc.find_one({"_id": ObjectId(obj_id)}))

    def find(self, filter_dict={}):
        for row in self.doc.find(filter_dict):
            print(row)

    def insert_one(self, data={}):
        res = self.doc.insert_one(data)
        print(res.inserted_id)

    def insert_many(self, data_list):
        return self.doc.insert_many(data_list)

    def upsert_many(self, filter_dict={}, data_list=[], options={'upsert': True}):
        '''
        有则更新，无则添加
        '''
        return self.doc.update_many(filter_dict, data_list, options)

    def upsert(self, data_list=[]):
        '''
        有则更新，无则添加
        '''
        ids = [data.pop("_id") for data in data_list]
        operations = [UpdateOne({"_id": idn}, {'$set': data}, upsert=True) for idn, data in zip(ids, data_list)]
        return self.doc.bulk_write(operations)

    def delete_one(self, filter_dict={}):
        self.doc.delete_one(filter_dict)

    def delete_many(self, filter_dict={}):
        self.doc.delete_many(filter_dict)

    def count_documents(self, filter_dict):
        return self.doc.count_documents(filter_dict)


def show_info():
    print("""
          i inset_one
          I insert_many
          f find_one
          fid find_by_objectid
          F find_all
          d delete_one
          D delete_all
          c count_documents
          Cc change_collection
          Cd change_db
          l list_collections
          L load_json_filter_dict
          """
          )


def test():
    mongo = MongoDb(**default_config)
    while True:
        try:
            show_info()
            ch = input("(exit)input choices:")
            if ch == 'exit' or ch == 'q':
                return True
            if ch == 'Cc':
                line = input("input collection_name:")
                mongo.change_collection(line)
                continue
            if ch == 'Cd':
                line = input("input db_name:")
                mongo.change_db(line)
                continue
            if ch == 'l':
                mongo.list_collections()
                continue
            if ch == 'L':
                line = input("input json_filter_dict_name:")
                mongo.load_json_filter_dict(line)
                continue
            if ch == "fid":
                line = input("input objectId:")
                mongo.find_by_objectid(line)
                continue

            line = input("input data:")
            data = json.loads(line) if line != "" else {}
            if ch == 'i':
                mongo.insert_one(data)
            if ch == 'I':
                lines = []
                while line != "exit":
                    lines.append(json.loads(line))
                    line = input("(exit)input data:")
                mongo.insert_many(lines)
            if ch == "f":
                mongo.find_one(data)
            if ch == 'F':
                mongo.find(data)
            if ch == 'd':
                mongo.delete_one(data)
            if ch == 'D':
                mongo.delete_many(data)
            if ch == 'c':
                print(mongo.count_documents(data))
        except Exception as e:
            print(str(e))


if __name__ == "__main__":
    test()
