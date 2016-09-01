# coding=utf-8
import traceback
from flask import current_app
from . import db
from sqlalchemy import or_


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stu_no = db.Column(db.String(64), nullable=False,
                       unique=True, index=True)
    name = db.Column(db.Unicode(128))
    department = db.Column(db.Unicode(128))
    major = db.Column(db.Unicode(128))
    grade = db.Column(db.String(32))

    def __repr__(self):
        return '<Student %s %s>' % (self.stu_no, self.name)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_json(self):
        return {
            'id': self.id,
            'stu_no':self.stu_no,
            'name': self.name,
            'department': self.department
        }


def get_by_id(id):
    return Student.query.filter(Student.id == id).first()
'''
add
'''

def get_by_stu_no(stu_no):
    return Student.query.filter(Student.stu_no == stu_no).first()


def get_all():
    return Student.query.all()
#
# 获取参加竞赛学生列表
#
#
def get_all_list(keyword=None):
    query = Student.query
    if keyword:
        keyword = '%' + keyword + '%'
        query = query.filter(or_(Student.stu_no.like(keyword),Student.department.like(keyword)))
    return query.all()


def get_count():
    return Student.query.count()


def get_list_pageable(page, per_page):
    return Student.query.order_by(Student.stu_no)\
        .paginate(page, per_page, error_out=False)


def create_student(student_form):
    try:
        has = get_by_stu_no(student_form.stu_no.data)
        if has:
            return u'当前学号的学生信息已存在'
        student = Student()
        student.stu_no = student_form.stu_no.data
        student.name = student_form.name.data
        student.department = student_form.department.data
        student.major = student_form.major.data
        student.grade = student_form.grade.data
        student.save()
        current_app.logger.info(u'录入学生 %r 成功', student)
        return 'OK'
    except Exception, e:
        current_app.logger.error(u'录入学生 %s 失败', student_form.stu_no.data)
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'


def update_student(student, student_form):
    try:
        has = get_by_stu_no(student_form.stu_no.data)
        if has and has.id != student.id:
            return u'当前学号的学生信息已存在'
        student.stu_no = student_form.stu_no.data
        student.name = student_form.name.data
        student.department = student_form.department.data
        student.major = student_form.major.data
        student.grade = student_form.grade.data
        student.save()
        current_app.logger.info(u'更新学生 %r 成功', student)
        return 'OK'
    except Exception, e:
        current_app.logger.error(u'更新学生 %r 失败', student)
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'


def delete_student(student):
    try:
        student.delete()
        current_app.logger.info(u'删除学生成功')
        return 'OK'
    except Exception:
        current_app.logger.error(u'删除学生失败')
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'
