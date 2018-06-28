# -*- coding:utf-8 -*-
import sys
import os.path
from statistic import StatisticExtractor
from predict import PredictionReportExtractor
from flask import Flask, request, url_for
from flask import jsonify
import time
import traceback
import store_period
from mongodb_util import ReportMongoUtill, KashuoMongoUtil1, KashuoMongoUtil2

mongo_util1 = KashuoMongoUtil1()

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

application = Flask(__name__)


@application.route('/store_report/statistic/<store_number>/<int:year>/<int:month>')
def get_statistic(store_number, year, month):
    """
    获取统计数据
    :param store_number;year;month
    :return:
    """
    result = {}

    try:
        r = ReportMongoUtill()
        if r.exist(store_number, year, month):
            k = KashuoMongoUtil2()
            data = k.get_payment_type(store_number, year, month)
            payment_type = {}
            for d in data:
                payment_type[d["_id"]] = d["count"]

            report = r.find_statistic(store_number, year, month)
            result["code"] = 1
            result['jiaoyibishu'] = report['jiaoyibishu']
            result['jiaoyizonge'] = report['jiaoyizonge']
            result['xiaofeirenshu'] = report['xiaofeirenshu']
            result['huoyueshijian'] = report['huoyueshijian']
            result['payment_type'] = payment_type
        else:
            s = StatisticExtractor()
            report = s.extract(store_number, year, month)
            result["code"] = 1
            result['jiaoyibishu'] = report['jiaoyibishu']
            result['jiaoyizonge'] = report['jiaoyizonge']
            result['xiaofeirenshu'] = report['xiaofeirenshu']
            result['huoyueshijian'] = report['huoyueshijian']
            result['payment_type'] = report['payment_type']
    except:
        traceback.print_exc()
        result["code"] = 0

    return jsonify(result)


@application.route('/store_report/history/<store_number>/<int:year>/<int:month>')
def get_history(store_number, year, month):
    """
    获取统计数据
    :param store_number;year;month
    :return:
    """
    result = {}

    try:
        r = ReportMongoUtill()
        history_list = r.get_history(store_number, year, month)
        result['history'] = history_list
    except:
        traceback.print_exc()
        result["code"] = 0

    return jsonify(result)


@application.route('/store_report/comparison/<store_number>/<int:year>/<int:month>')
def get_comparison(store_number, year, month):
    """
    获取横向对比数据
    :param store_number:
    :return:
    """
    result = {}

    try:
        r = ReportMongoUtill()
        info = mongo_util1.get_store_info(store_number)
        c = None
        for d in info:
            c = d['category']
        data = r.find_comparision_statistic(c, year, month)

        avg_xiaofeirenshu = 0
        avg_jiaoyizonge = 0.
        avg_jiaoyibishu = 0

        for d in data:
            avg_xiaofeirenshu = d["avg_xiaofeirenshu"]
            avg_jiaoyizonge = d["avg_jiaoyizonge"]
            avg_jiaoyibishu = d["avg_jiaoyibishu"]

        result = {"code": 1,
                  "avg_xiaofeirenshu": avg_xiaofeirenshu,
                  "avg_jiaoyizonge": avg_jiaoyizonge,
                  "avg_jiaoyibishu": avg_jiaoyibishu}
    except:
        traceback.print_exc()
        result["code"] = 0

    return jsonify(result)


@application.route('/store_report/predict/<store_number>/<int:year>/<int:month>')
def get_predict(store_number, year, month):
    """
    获取预测数据
    :param store_number:
    :return:
    """
    result = {}

    try:
        r = ReportMongoUtill()
        month_long = 24 * 3600 * 31
        a_month_ago = time.time() - month_long
        if time.localtime()[0] == year and time.localtime()[1] == month:
            e = PredictionReportExtractor()
            report = e.extract(r.get_history(store_number, year, month))
        elif time.localtime(a_month_ago)[0] == year and time.localtime(a_month_ago)[1] == month:
            e = PredictionReportExtractor()
            report = e.extract(r.get_history(store_number, year, month))
        else:
            x1 = 0
            x2 = 0.
            if r.exist(store_number, year, month+1):
                temp = r.find_statistic(store_number, year, month+1)
                x1 += temp['xiaofeirenshu']
                x2 += temp['jiaoyizonge']
            report = {'predict_customer': x1, 'predict_revenue': x2}
        result["code"] = 1
        result["predict"] = report
    except:
        traceback.print_exc()
        result["code"] = 0

    return jsonify(result)


@application.route('/mall_report/statistic/<int:mall_id>/<int:year>/<int:month>')
def get_mall_statistic(mall_id, year, month):

    result = {}

    try:
        r = ReportMongoUtill()
        k = KashuoMongoUtil2()
        data = r.fetch_mall_statistic(mall_id, year, month)

        xiaofeirenshu = len(k.get_mall_consumers(mall_id, year, month))
        jiaoyizonge = 0.
        huoyueshijian = [0] * 6
        for d in data:
            jiaoyizonge += d['jiaoyizonge']
            for i in range(6):
                huoyueshijian[i] += d['huoyueshijian'][i]

        jiaoyibishu = 0
        payment_type = {}
        pt = k.get_mall_payment_type(mall_id, year, month)
        for d in pt:
            payment_type[d["_id"]] = d["count"]
            jiaoyibishu += d["count"]

        result = {'xiaofeirenshu': xiaofeirenshu,
                  'huoyueshijian': huoyueshijian,
                  'jiaoyizonge': jiaoyizonge,
                  'payment_type': payment_type,
                  'jiaoyibishu': jiaoyibishu,
                  'code': 1}

    except:
        traceback.print_exc()
        result["code"] = 0

    return jsonify(result)


@application.route('/mall_report/rank/<int:mall_id>/<int:year>/<int:month>')
def get_mall_rank(mall_id, year, month):

    result = {}

    try:
        r = ReportMongoUtill()
        data = r.fetch_mall_statistic(mall_id, year, month)
        stores_data = []

        for d in data:
            xiaofeirenshu = d['xiaofeirenshu']
            jiaoyizonge = d['jiaoyizonge']
            jiaoyibishu = d['jiaoyibishu']

            name = mongo_util1.get_store_name(d['store_number'])
            stat = {'name': name,
                    'xiaofeirenshu': xiaofeirenshu,
                    'jiaoyizonge': jiaoyizonge,
                    'jiaoyibishu': jiaoyibishu}

            stores_data.append(stat)

        result['code'] = 1
        result['rank'] = stores_data

    except:
        result['code'] = 0
        traceback.print_exc()

    return jsonify(result)


@application.route('/bank/frequency/<store_number>')
def get_frequency(store_number):

    result = {}

    try:
        temp = store_period.get_period(store_number)
        result['frequency'] = temp[0]
        result['attend'] = temp[1]
        result['code'] = 1
    except:
        traceback.print_exc()
        result['code'] = 0

    return jsonify(result)


@application.route('/quanwang/zhifufangshi/<int:year>/<int:month>')
def get_payment_type(year, month):
    result = {}

    try:
        k = KashuoMongoUtil2()
        data = k.get_3m_payment_type(year, month)

        jiaoyibishu = {}

        for d in data:
            jiaoyibishu[d["_id"]] = d["count"]

        result['code'] = 1
        result['zhifufangshi'] = jiaoyibishu

    except:
        result['code'] = 0

    return jsonify(result)


@application.route('/quanwang/mall_rank/<int:year>/<int:month>')
def get_all_rank(year, month):
    result = {}

    try:
        k = KashuoMongoUtil2()

        all_mall = {}

        data = k.quanwang_rank(year, month)

        for mall in data:
            all_mall[mall["_id"]] = mall["count"]

        result['code'] = 1
        result['rank_info'] = all_mall

    except:
        result['code'] = 0

    return jsonify(result)

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8080, debug=True)
