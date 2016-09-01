# coding=utf-8
import traceback
from flask import current_app
from . import db, Resource


class ContestSeries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(256), unique=True, nullable=False)
    budget_text = db.Column(db.Unicode(2048))

    def __repr__(self):
        return '<ContestSeries %s>' % self.name

    def save(self):
        db.session.add(self)
        db.session.commit()

    def remove(self):
        db.session.delete(self)
        db.session.commit()


def get_by_id(id):
    return ContestSeries.query.filter(ContestSeries.id == id).first()


def get_by_name(name):
    return ContestSeries.query.filter(ContestSeries.name == name).first()


def get_all():
    return ContestSeries.query.all()


def get_count():
    return ContestSeries.query.count()


def get_list_pageable(page, per_page):
    return ContestSeries.query.order_by(ContestSeries.id)\
        .paginate(page, per_page, error_out=False)


def create_series(series_form):
    try:
        has_series = get_by_name(series_form.name.data)
        if has_series:
            current_app.logger.warning(u'竞赛系列 %s 已存在', series_form.name.data)
            return 'FAIL'
        series = ContestSeries()
        series.name = series_form.name.data
        series.budget_text = series_form.budget_text.data
        series.save()
        current_app.logger.info(u'录入竞赛系列 %s 成功', series.name)
        return 'OK'
    except Exception, e:
        current_app.logger.error(u'录入竞赛系列 %s 失败', series_form.name.data)
        current_app.logger.error(e)
        return 'FAIL'


def update_series(series, series_form):
    try:
        series.name = series_form.name.data
        series.budget_text = series_form.budget_text.data
        series.save()
        current_app.logger.info(u'更新竞赛系列 %s 成功', series.name)
        return 'OK'
    except Exception, e:
        current_app.logger.error(u'更新竞赛系列 %s 失败', series_form.name.data)
        current_app.logger.error(e)
        return 'FAIL'


def delete_series(series):
    try:
        for contest in series.contests.all():
            for awards in contest.awards.all():
                for res in awards.resources.all():
                    Resource.delete_res(res)
        series.remove()
        current_app.logger.info(u'删除竞赛系列成功')
        return 'OK'
    except Exception:
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'
