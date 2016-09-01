# coding=utf-8

import traceback
from flask import current_app
from . import db


class ContestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(32), unique=True, nullable=False)
    budget_text = db.Column(db.Unicode(2048))
    cid = db.Column(db.Integer)

    def __repr__(self):
        return '<ContestResult %s>' % self.name
    def save(self):
        db.session.add(self)
        db.session.commit()

    def remove(self):
        db.session.delete(self)
        db.session.commit()

def get_by_id(id):
    return ContestResult.query.filter(ContestResult.id == id).first()

def get_by_name(name):
    return ContestResult.query.filter(ContestResult.name == name).first()

def get_count():
    return ContestResult.query.count()

def get_list_pageable(page, per_page):
    return ContestResult.query.order_by(ContestResult.id)\
        .paginate(page, per_page, error_out=False)

def get_all():
    return ContestResult.query.order_by(ContestResult.cid.asc()).all()

def get_all_1(keyword=None):
    query = ContestResult.query
    if keyword:
        keyword = '%' + keyword + '%'
        query = query.filter((ContestResult.name.like(keyword)))
    return query.all()

def get_new_list(t,id):
    count = ContestResult.query.count()
    id_list = []
    for next in range(count):
        id_list.append(next + 1)
    result_id = ContestResult.query.filter(ContestResult.id == id).first()
    temp = result_id.cid
    if int(t) == int(1):
        fid = id_list[id_list.index(temp) - 1]
        result_front_id = ContestResult.query.filter(ContestResult.cid == fid).first()
    if int(t) == int(2):
        nid = id_list[id_list.index(temp) + 1]
        result_next_id = ContestResult.query.filter(ContestResult.cid == nid).first()

    if int(t) == int(1):
        result_id.cid = id_list[id_list.index(temp) - 1]
        result_id.save()
        result_front_id.cid = id_list[id_list.index(temp)]
        result_front_id.save()
    if int(t) == int(2):
        result_id.cid = id_list[id_list.index(temp) + 1]
        result_id.save()
        result_next_id.cid = id_list[id_list.index(temp)]
        result_next_id.save()
    return id_list

def create_result(result_form):
    try:
        has_result = get_by_name(result_form.name.data)
        if has_result:
            current_app.logger.warning(u'竞赛档次 %s 已存在', result_form.name.data)
            return 'FAIL'
        result = ContestResult()
        result.name = result_form.name.data
        result.budget_text = result_form.budget_text.data
        result.cid = int(get_count()) + int(1)
        result.save()
        current_app.logger.info(u'录入竞赛档次 %s 成功', result.name)
        return 'OK'
    except Exception, e:
        current_app.logger.error(u'录入竞赛档次 %s 失败', result_form.name.data)
        current_app.logger.error(e)
        return 'FAIL'


def update_result(result, result_form):
    try:
        result.name = result_form.name.data
        result.budget_text = result_form.budget_text.data
        result.save()
        current_app.logger.info(u'更新竞赛系列 %s 成功', result.name)
        return 'OK'
    except Exception, e:
        current_app.logger.error(u'更新竞赛系列 %s 失败', result_form.name.data)
        current_app.logger.error(e)
        return 'FAIL'


def delete_result(result):
    try:
        result.remove()
        current_app.logger.info(u'删除竞赛档次成功')
        result_list = ContestResult.query.order_by(ContestResult.cid.asc()).all()
        count = ContestResult.query.count()
        list = []
        for c in range(count):
            list.append(int(c + 1))
        j = 0
        for next in result_list:
            result_list[j].cid = list[j]
            result_list[j].save()
            j = j + 1
        return 'OK'
    except Exception:
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'