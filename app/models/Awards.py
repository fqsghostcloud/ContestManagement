# coding=utf-8
import traceback
from flask import current_app
from . import db, Contest, Resource, Student, AwardsLevel
from collections import Counter

awards_teacher = db.Table('awards_teacher',
    db.Column('awards', db.String(128), db.ForeignKey('awards.awards_id', ondelete="CASCADE")),
    db.Column('teacher', db.Integer, db.ForeignKey('teacher.id', ondelete="CASCADE"))
)

awards_student = db.Table('awards_student',
    db.Column('awards', db.String(128), db.ForeignKey('awards.awards_id', ondelete="CASCADE")),
    db.Column('student', db.String(64), db.ForeignKey('student.stu_no', ondelete="CASCADE"))
)



AwardsType = [
    u'个人',
    u'团体'
]

AwardsProcess = [
    u'已录入',
    u'已审核'
]

AwardsResult = [
    u'一档',
    u'二档',
    u'三档',
    u'四档'
]

class Awards(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    awards_id = db.Column(db.String(128), nullable=False,
                          unique=True, index=True)
    honor = db.Column(db.Unicode(128))
    level = db.Column(db.Unicode(128))
    title = db.Column(db.Unicode(512))
    type = db.Column(db.Unicode(32))
    process = db.Column(db.Unicode(64), default=AwardsProcess[0])
    result = db.Column(db.Unicode(64))
    apply = db.Column(db.Integer)
    department = db.Column(db.Unicode(128))
    year = db.Column(db.Unicode(128))
    contest_id = db.Column(db.String(128),
                           db.ForeignKey('contest.contest_id', ondelete='CASCADE',
                                         onupdate='CASCADE'), nullable=False)
    contest = db.relationship('Contest',
                             backref=db.backref('awards',
                                                cascade="all, delete-orphan",
                                                passive_deletes=True,
                                                lazy='dynamic'))
    #many to many Awards<-->Teacher
    teachers = db.relationship('Teacher',
                               secondary=awards_teacher,
                               backref=db.backref('awards', lazy='dynamic'))
    #many to many Awards<-->Student
    students = db.relationship('Student',
                               secondary=awards_student,
                               backref=db.backref('awards', lazy='dynamic'))

    def __repr__(self):
        return '<Awards %s>' % self.awards_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    def remove(self):
        db.session.delete(self)
        db.session.commit()

def generate_next_awards_id(contest):
    ''' generate next awards id for the new awards '''
    last_awards = contest.awards.order_by(Awards.awards_id.desc())\
        .with_lockmode('update').first()
    contest_id = contest.contest_id
    if last_awards == None:
        return '%s%s' % (contest_id, '001')
    else:
        last_awards_id = int(last_awards.awards_id[8:])
        new_id = str(last_awards_id + 1)
        return '%s%s' % (contest_id, new_id.rjust(3, '0'))

def get_by_id(id):
    return Awards.query.filter(Awards.id == id).first()

def get_list_by_contest_id(cid):
    return Awards.query.filter(Awards.contest_id == cid).all()

def get_all():
    return Awards.query.all()

def get_level_by_level():
    awards_list = []
    awards = Awards.query.all()
    for a in awards:
        if not a.level in awards_list:
            awards_list.append(a.level)
    level = AwardsLevel.get_all()
    levels = []
    for l in level:
        for a in awards_list:
            if l.name == a:
                levels.append(l.name)
    return levels

def get_awards_num(level_selected):
    from datetime import date
    year_now = date.today().year
    year_select = [str(year) for year in range(year_now-4,year_now+1)]
    awards = Awards.query.all()
    level = AwardsLevel.get_all()
    level_list = []
    list = []
    if level_selected != u'所有':
        for l in level:
            if level_selected in l.name:
                for a in awards:
                    if l.name == a.level and not l.name in level_list:
                        level_list.append(l.name)
        for y in year_select:
            for l in level_list:
                number = 0
                for a in awards:
                    if a.year == y and a.level == l:
                        number = number + 1
                list.append(number)
    else:
        for l in level:
            for a in awards:
                if a.level == l.name and not l.name in level_list:
                    level_list.append(l.name)
        for y in year_select:
            for l in level_list:
                number = 0
                for a in awards:
                    if a.year == y and a.level == l:
                        number = number + 1
                list.append(number)
    return list

def get_awards_num2(year,level_selected):
    list = []
    department = []
    awards = Awards.query.all()
    for a in awards:
        if not a.department in department:
            department.append(a.department)
    level = AwardsLevel.get_all()
    level_list = []
    if level_selected != u'所有':
        for l in level:
            if level_selected in l.name:
                for a in awards:
                    if l.name == a.level and not l.name in level_list:
                        level_list.append(l.name)
                        print l.name
        for d in department:
            for l in level_list:
                number = 0
                for a in awards:
                    if a.level == l and a.department == d and int(a.year) == int(year):
                        number = number + 1
                list.append(number)
    else:
        for l in level:
            for a in awards:
                if l.name == a.level and not l.name in level_list:
                    level_list.append(l.name)
        for d in department:
            for l in level_list:
                number = 0
                for a in awards:
                    if a.level == l and a.department == d and int(a.year) == int(year):
                        number = number + 1
                list.append(number)
    return list

def get_level_by_year():
    awards = Awards.query.all()
    i = 0
    j = 0
    year_list = []
    for a in awards:
        year_list.append(awards[i].year)
        year_list.append(awards[j].level)
        i = i + 1
        j = j + 1
    return year_list

#
#提交编辑
#
def set_all_apply_to_zero(contest_id):
    n= 0
    awards = Awards.query.filter(Awards.contest_id == contest_id).all()
    for a in awards:
        awards[n].apply = int(0)
        awards[n].process = u'待审核'
        n = n + 1

#
#奖项审核通过
#
def set_all_apply(contest_id):
    n = 0
    awards = Awards.query.filter(Awards.contest_id == contest_id).all()
    for a in awards:
        awards[n].apply = int(1)
        awards[n].process = u'已审核'
        n = n + 1
#
#显示有新提交
#
# def get_result(awards_id):
#     n = 0
#     awards = Awards
#
#奖项审核不通过
#
def set_all_apply_refuse(contest_id):
    n = 0
    awards = Awards.query.filter(Awards.contest_id == contest_id).all()
    print 111111111
    for a in awards:
        awards[n].apply = int(5)
        awards[n].process = u'审核不通过'
        n = n + 1

#
#奖项申请编辑
#
def set_all_apply_edit(contest_id):
    m = 0
    awards = Awards.query.filter(Awards.contest_id == contest_id).all()
    for a in awards:
        awards[m].apply = int(2)
        m = m + 1
#
#奖项申请编辑审核通过
#
def set_all_apply_through(contest_id):
    n = 0
    awards = Awards.query.filter(Awards.contest_id == contest_id).all()
    for a in awards:
        awards[n].apply = 3
        n = n + 1
#
#添加新奖项
#
# def set_new_apply(contest_id):
#     awards = Awards.query.filter(Awards.contest_id == contest_id).all()
#     awards.apply = 0
#     awards.process = u'已录入'

def get_count(contest_id = -1, level = -1):
    query = Awards.query
    if contest_id != -1:
        query = query.filter(Awards.contest_id == contest_id)
    if level != -1:
        query = query.filter(Awards.process == AwardsProcess[level - 2])
    return query.count()

def getccccccc():
    query = Awards.query
    return query.count()

def get_list_pageable(page, per_page, contest_id = -1, level = -1):
    query = Awards.query
    if contest_id != -1:
        query = query.filter(Awards.contest_id == contest_id)
    if level != -1:
        query = query.filter(Awards.process == AwardsProcess[level - 2])
    return query.order_by(Awards.awards_id)\
        .paginate(page, per_page, error_out=False)

def create_awards(awards_form, contest, files):
    try:

        awards = Awards()
        awards.awards_id = generate_next_awards_id(contest)
        awards.level = awards_form.level.data
        awards.apply = 0
        awards.honor = awards_form.honor.data
        awards.title = awards_form.title.data
        awards.type = awards_form.type.data
        current_app.logger.info(getccccccc())
        awards.contest = contest
        awards.year = awards_form.year.data
        awards.department = awards_form.department.data
        awards.teachers = awards_form.get_teacher_list()
        # if awards.teachers == []:
        #     return 'notTch'
        awards.students = awards_form.get_student_list()
        # if awards.students == []:
        #
        #     return 'notStu'
        awards.save()
        current_app.logger.info(u'录入奖项 %s 成功', awards.awards_id)
        for name, file in files.items(multi=True):
           Resource.save_res(file, awards)
        current_app.logger.info(u'上传奖项附件成功')
        return 'OK'
    except Exception:
        current_app.logger.error(u'录入奖项 %r 失败', awards_form)
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'

def update_awards(awards, awards_form, files):
    try:
        awards.level = awards_form.level.data
        awards.year = awards_form.year.data
        awards.honor = awards_form.honor.data
        awards.title = awards_form.title.data
        awards.type = awards_form.type.data
        awards.teachers = awards_form.get_teacher_list()
        awards.students = awards_form.get_student_list()
        awards.apply = 6
        awards.process = u'待审核'
        awards.save()
        current_app.logger.info(u'更新奖项 %s 成功', awards.awards_id)
        for name, file in files.items(multi=True):
            Resource.save_res(file, awards)
        current_app.logger.info(u'上传奖项附件成功')
        return 'OK'
    except Exception:
        current_app.logger.error(u'更新奖项 %r 失败', awards_form)
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'


def delete_awards(awards):
    try:
        awards.remove()
        current_app.logger.info(u'删除奖项成功')
        return 'OK'
    except Exception:
        current_app.logger.error(u'删除奖项失败')
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'


def pass_awards(awards, opt, result):
    try:
        if opt == 1:
            awards.process = AwardsProcess[opt]
            awards.save()
            current_app.logger.info(u'审核奖项成功')
            return 'OK'
        elif opt == 2:
            if not (0 <= result < 4):
                return u'非法操作'
            awards.process = AwardsProcess[opt]
            awards.level = AwardsResult[result]
            awards.save()
            current_app.logger.info(u'审核奖项成功')
            return 'OK'
        else:
            return u'非法操作'
    except Exception:
        current_app.logger.error(u'审核奖项错误')
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'

def LevelList():
    AwardsLevelList = []
    levels = AwardsLevel.get_all()
    for l in levels:
        AwardsLevelList.append(l.name)
    return AwardsLevelList

'''
add
'''

