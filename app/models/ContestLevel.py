# coding=utf-8
import traceback
from flask import current_app
from . import db

class ContestLevel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(256), unique=True, nullable=False)
    budget_text = db.Column(db.Unicode(2048))
    cid = db.Column(db.Integer)
    def __repr__(self):
        return '<ContestLevel %s>' % self.name

    def save(self):
        db.session.add(self)
        db.session.commit()

    def remove(self):
        db.session.delete(self)
        db.session.commit()


def get_by_id(id):
    return ContestLevel.query.filter(ContestLevel.id == id).first()

def get_by_name(name):
    return ContestLevel.query.filter(ContestLevel.name == name).first()


def get_all():
    return ContestLevel.query.order_by(ContestLevel.cid.asc()).all()


def get_count():
    return ContestLevel.query.count()


def get_list_pageable(page, per_page):
    return ContestLevel.query.order_by(ContestLevel.id)\
        .paginate(page, per_page, error_out=False)

def get_new_list(t,id):
    count = ContestLevel.query.count()
    id_list = []
    for next in range(count):
        id_list.append(next + 1)
    contest_id = ContestLevel.query.filter(ContestLevel.id == id).first()
    temp = contest_id.cid
    if int(t) == int(1):
        fid = id_list[id_list.index(temp) - 1]
        contest_front_id = ContestLevel.query.filter(ContestLevel.cid == fid).first()
    if int(t) == int(2):
        nid = id_list[id_list.index(temp) + 1]
        contest_next_id = ContestLevel.query.filter(ContestLevel.cid == nid).first()

    if int(t) == int(1):
        contest_id.cid = id_list[id_list.index(temp) - 1]
        contest_id.save()
        contest_front_id.cid = id_list[id_list.index(temp)]
        contest_front_id.save()
    if int(t) == int(2):
        contest_id.cid = id_list[id_list.index(temp) + 1]
        contest_id.save()
        contest_next_id.cid = id_list[id_list.index(temp)]
        contest_next_id.save()
    return id_list

def create_level(level_form):
    try:
        has_series = get_by_name(level_form.name.data)
        if has_series:
            current_app.logger.warning(u'竞赛等级 %s 已存在', level_form.name.data)
            return 'FAIL'
        level = ContestLevel()
        level.name = level_form.name.data
        level.budget_text = level_form.budget_text.data
        level.cid = int(get_count()) + int(1)
        level.save()
        current_app.logger.info(u'录入竞赛等级 %s 成功', level.name)
        return 'OK'
    except Exception, e:
        current_app.logger.error(u'录入竞赛等级 %s 失败', level_form.name.data)
        current_app.logger.error(e)
        return 'FAIL'


def update_level(level, level_form):
    try:
        level.name = level_form.name.data
        level.budget_text = level_form.budget_text.data
        level.save()
        current_app.logger.info(u'更新竞赛系列 %s 成功', level.name)
        return 'OK'
    except Exception, e:
        current_app.logger.error(u'更新竞赛系列 %s 失败', level_form.name.data)
        current_app.logger.error(e)
        return 'FAIL'

def delete_level(level):
    try:
        level.remove()
        current_app.logger.info(u'删除竞赛等级成功')
        level_list = ContestLevel.query.order_by(ContestLevel.cid.asc()).all()
        count = ContestLevel.query.count()
        list = []
        for c in range(count):
            list.append(int(c + 1))
        j = 0
        for next in level_list:
            level_list[j].cid = list[j]
            level_list[j].save()
            j = j + 1
        return 'OK'
    except Exception:
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'

