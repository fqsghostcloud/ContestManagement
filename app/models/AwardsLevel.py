# coding=utf-8
import traceback
from flask import current_app
from . import db

class AwardsLevel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(256), unique=True, nullable=False)
    budget_text = db.Column(db.Unicode(2048))
    aid = db.Column(db.Integer)

    def __repr__(self):
        return '<AwardsSeries %s>' % self.name

    def save(self):
        db.session.add(self)
        db.session.commit()

    def remove(self):
        db.session.delete(self)
        db.session.commit()


def get_by_id(id):
    return AwardsLevel.query.filter(AwardsLevel.id == id).first()


def get_by_name(name):
    return AwardsLevel.query.filter(AwardsLevel.name == name).first()


def get_all():
    return AwardsLevel.query.order_by(AwardsLevel.aid.asc()).all()


def get_count():
    return AwardsLevel.query.count()


def get_list_pageable(page, per_page):
    return AwardsLevel.query.order_by(AwardsLevel.id)\
        .paginate(page, per_page, error_out=False)

def get_new_list(t,id):
    count = AwardsLevel.query.count()
    id_list = []
    for next in range(count):
        id_list.append(next + 1)
    level_id = AwardsLevel.query.filter(AwardsLevel.id == id).first()
    temp = level_id.aid
    if int(t) == int(1):
        fid = id_list[id_list.index(temp) - 1]
        level_front_id = AwardsLevel.query.filter(AwardsLevel.aid == fid).first()
    if int(t) == int(2):
        nid = id_list[id_list.index(temp) + 1]
        level_next_id = AwardsLevel.query.filter(AwardsLevel.aid == nid).first()

    if int(t) == int(1):
        level_id.aid = id_list[id_list.index(temp) - 1]
        level_id.save()
        level_front_id.aid = id_list[id_list.index(temp)]
        level_front_id.save()
    if int(t) == int(2):
        level_id.aid = id_list[id_list.index(temp) + 1]
        level_id.save()
        level_next_id.aid = id_list[id_list.index(temp)]
        level_next_id.save()
    return id_list

def create_level(level_form):
    try:
        has_series = get_by_name(level_form.name.data)
        if has_series:
            current_app.logger.warning(u'奖项等级 %s 已存在', level_form.name.data)
            return 'FAIL'
        level = AwardsLevel()
        level.name = level_form.name.data
        level.budget_text = level_form.budget_text.data
        level.aid = int(get_count()) + int(1)
        level.save()
        current_app.logger.info(u'录入奖项等级 %s 成功', level.name)
        return 'OK'
    except Exception, e:
        current_app.logger.error(u'录入奖项等级 %s 失败', level_form.name.data)
        current_app.logger.error(e)
        return 'FAIL'


def update_level(level, level_form):
    try:
        level.name = level_form.name.data
        level.budget_text = level_form.budget_text.data
        level.save()
        current_app.logger.info(u'更新奖项等级 %s 成功', level.name)
        return 'OK'
    except Exception, e:
        current_app.logger.error(u'更新奖项等级 %s 失败', level_form.name.data)
        current_app.logger.error(e)
        return 'FAIL'

def delete_level(level):
    try:
        level.remove()
        current_app.logger.info(u'删除奖项等级成功')
        level_list = AwardsLevel.query.order_by(AwardsLevel.aid.asc()).all()
        count = AwardsLevel.query.count()
        list = []
        for c in range(count):
            list.append(int(c + 1))
        j = 0
        for next in level_list:
            level_list[j].aid = list[j]
            level_list[j].save()
            j = j + 1
        return 'OK'
    except Exception:
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'

