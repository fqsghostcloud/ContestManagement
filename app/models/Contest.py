# coding=utf-8
import traceback
from flask import current_app
from . import db, ContestSeries, Resource,ContestLevel,ContestResult
from datetime import date
from collections import Counter

ContestType = [
    u'学科竞赛',
    u'体育竞赛',
    u'创新创业竞赛',
    u'其它'
]

ContestResultList = [
    u'未定档',
]
class Contest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contest_id = db.Column(db.String(128), unique=True,
                           nullable=False, index=True)
    name_cn = db.Column(db.Unicode(512))
    name_en = db.Column(db.String(512))
    #level = db.Column(db.Unicode(32))   # 竞赛等级
    result = db.Column(db.Unicode(32))  # 竞赛审核结果
    type = db.Column(db.Unicode(32))    # 竞赛类型
    department = db.Column(db.Unicode(128))
    organizer = db.Column(db.Unicode(512))
    co_organizer = db.Column(db.Unicode(512))
    year = db.Column(db.Integer)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    place = db.Column(db.Unicode(1024))
    site = db.Column(db.String(1024))
    budget = db.Column(db.Float)
    budget_text = db.Column(db.Unicode(2048))
    student_num = db.Column(db.Integer)
    teacher_num = db.Column(db.Integer)
    #subject = db.Column(db.Unicode(512))
    apply = db.Column(db.Unicode(12))   #申请编辑
    series_name = db.Column(db.Unicode(256),
                            db.ForeignKey('contest_series.name', ondelete="CASCADE"),
                            nullable=True)
    series = db.relationship('ContestSeries',
                             backref=db.backref('contests',
                                                cascade="all, delete-orphan",
                                                passive_deletes=True,
                                                lazy='dynamic'))
    level_name = db.Column(db.Unicode(256),
                            db.ForeignKey('contest_level.name', ondelete="CASCADE"),
                            nullable=True)
    level = db.relationship('ContestLevel',
                             backref=db.backref('contests',
                                                cascade="all, delete-orphan",
                                                passive_deletes=True,
                                                lazy='dynamic'))

    def __repr__(self):
        return '<Contest %s %s>' % (self.contest_id, self.name_cn)

    @property
    def is_pass(self):
        return self.result and self.result != ContestResultList[0]

    def save(self):
        db.session.add(self)
        db.session.commit()

    def remove(self):
        db.session.delete(self)
        db.session.commit()


def generate_next_contest_id(year):
    ''' generate next contest id for the new contest's year '''
    last_contest = Contest.query.filter(Contest.year == year)\
        .order_by(Contest.contest_id.desc())\
        .with_lockmode('update').first()
    if last_contest == None:
        return 'W%d%s' % (year, '001')
    else:
        last_contest_id = int(last_contest.contest_id[6:])
        new_id = str(last_contest_id + 1)
        return 'W%d%s' % (year, new_id.rjust(3, '0'))

def get_all():
    return Contest.query.count()

def get_alls():
    return Contest.query.all()


def get_dep(department):
    return Contest.query.filter(Contest.department == department).count()

def get_by_id(id):
    return Contest.query.filter(Contest.id == id).first()
#
#按奖项编号并排序
#
def get_year():
    year = []
    contest = Contest.query.all()
    n = 0
    for num in contest:
        year.append(contest[n].year)
        n = n + 1
    counter = Counter(year)
    return counter

def get_count(filter_pass=0, department=None):
    query = Contest.query
    if filter_pass == 1:
        query = query.filter(Contest.result == None)
    elif filter_pass == -1:
        query = query.filter(Contest.result != None)
    if department:
        query = query.filter(Contest.department == department)
    return query.count()


def get_list_pageable(page=1, per_page=20, filter_pass=0, department=None,year = None):
    query = Contest.query
    if filter_pass == 1:
        query = query.filter(Contest.result == None)
    elif filter_pass == -1:
        query = query.filter(Contest.result != None)
    if department:
        query = query.filter(Contest.department == department)
    # if year:
    #     query = query.filter(Contest.year == year)
    if page == -1:
        return query.order_by(Contest.id).all()
    return query.order_by(Contest.id)\
        .paginate(page, per_page, error_out=False)


def create_contest(contest_form, request):
    # from datetime import date
    try:
        contest = Contest()
        contest.contest_id = generate_next_contest_id(int(contest_form.date_range.data[0][0:4]))
        contest.name_cn = contest_form.name_cn.data
        contest.name_en = contest_form.name_en.data
        #contest.level = contest_form.level_id.data
        #contest.result = ContestResult[0]
        contest.apply = 0
        contest.type = contest_form.type.data
        contest.department = contest_form.department.data
        contest.site = contest_form.site.data
        contest.organizer = contest_form.organizer.data
        contest.co_organizer = contest_form.co_organizer.data
        contest.year = int(contest_form.date_range.data[0][0:4])
        contest.start_date = contest_form.date_range.data[0]
        contest.end_date = contest_form.date_range.data[1]
        contest.budget = contest_form.budget.data
        contest.budget_text = contest_form.budget_text.data
        contest.student_num = contest_form.student_num.data
        contest.teacher_num = contest_form.teacher_num.data
        # contest.subject = contest_form.subject.data
        city = request.form.get('prov', '') + \
               request.form.get('city', '') + \
               request.form.get('dist', '')
        contest.place = city + contest_form.place.data
        level = ContestLevel.get_by_id(contest_form.level_id.data)
        if level:
            contest.level = level
        series = ContestSeries.get_by_id(contest_form.series_id.data)
        if series:
            contest.series = series
        contest.save()
        current_app.logger.info(u'录入竞赛 %s 成功', contest.name_cn)
        return 'OK'
    except Exception:
        current_app.logger.error(u'录入竞赛 %s 失败', contest_form.name_cn.data)
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'


def update_contest(contest, contest_form, request):
    try:
        contest.name_cn = contest_form.name_cn.data
        contest.name_en = contest_form.name_en.data
        # contest.level = contest_form.level.data
        contest.type = contest_form.type.data
        contest.type = contest_form.type.data
        contest.department = contest_form.department.data
        contest.site = contest_form.site.data
        contest.organizer = contest_form.organizer.data
        contest.co_organizer = contest_form.co_organizer.data
        # contest.year = contest_form.year.data
        contest.start_date = contest_form.date_range.data[0]
        contest.end_date = contest_form.date_range.data[1]
        contest.budget = contest_form.budget.data
        contest.budget_text = contest_form.budget_text.data
        contest.student_num = contest_form.student_num.data
        contest.teacher_num = contest_form.teacher_num.data
        # contest.subject = contest_form.subject.data
        city = request.form.get('prov', '') + \
               request.form.get('city', '') + \
               request.form.get('dist', '')
        contest.place = city + contest_form.place.data
        series = ContestSeries.get_by_id(contest_form.series_id.data)
        if series:
            contest.series = series
        contest.save()
        current_app.logger.info(u'更新竞赛 %s 成功', contest.name_cn)
        return 'OK'
    except Exception:
        current_app.logger.error(u'更新竞赛 %s 失败', contest_form.name_cn.data)
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'


def delete_contest(contest):
    try:
        for awards in contest.awards.all():
            for res in awards.resources.all():
                Resource.delete_res(res)
        contest.remove()
        current_app.logger.info(u'删除竞赛成功')
        return 'OK'
    except Exception:
        current_app.logger.error(u'删除竞赛失败')
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'

def ResultList():
    ContestResultList = []
    results = ContestResult.get_all()
    for r in results:
         ContestResultList.append(r)
         current_app.logger.info(r)
    return ContestResultList

