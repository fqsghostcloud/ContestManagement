# coding=utf-8
import traceback
from flask import current_app
from . import db
from sqlalchemy import or_



class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(128))
    department = db.Column(db.Unicode(128))

    def __repr__(self):
        return '<Teacher %s>' % self.name

    def save(self):
        db.session.add(self)
        db.session.commit()

    def remove(self):
        db.session.delete(self)
        db.session.commit()

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'department': self.department
        }


def get_by_id(id):
    return Teacher.query.filter(Teacher.id == id).first()

def get_by_name(name):
    return Teacher.query.filter(Teacher.name == name).first()

def get_list_by_name(name):
    return Teacher.query.filter(Teacher.name == name).all()

def get_all():
    return Teacher.query.all()

def is_exist(name, department):
    has = Teacher.query.filter(Teacher.name == name
                               and Teacher.department == department).first()
    return has != None


def get_list_by_department(department):
    return Teacher.query.filter(Teacher.department == department).all()


def get_all(keyword=None):
    query = Teacher.query
    if keyword:
        keyword = '%' + keyword + '%'
        query = query.filter(or_(Teacher.name.like(keyword), Teacher.department.like(keyword)))
    return query.all()


def get_count():
    return Teacher.query.count()


def get_list_pageable(page, per_page):
    return Teacher.query.order_by(Teacher.id)\
        .paginate(page, per_page, error_out=False)


def create_teacher(teacher_form):
    try:
        teacher = Teacher()
        teacher.name = teacher_form.name.data
        teacher.department = teacher_form.department.data
        teacher.save()
        current_app.logger.info(u'录入教师 %s 成功', teacher.name)
        return 'OK'
    except Exception, e:
        current_app.logger.error(u'录入教师 %s 失败', teacher_form.name.data)
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'


def update_teacher(teacher, teacher_form):
    try:
        teacher.name = teacher_form.name.data
        teacher.department = teacher_form.department.data
        teacher.save()
        current_app.logger.info(u'更新教师 %s 成功', teacher.name)
        return 'OK'
    except Exception, e:
        current_app.logger.error(u'更新教师 %s 失败', teacher_form.name.data)
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'


def delete_teacher(teacher):
    try:
        teacher.remove()
        current_app.logger.info(u'删除教师成功')
        return 'OK'
    except Exception:
        current_app.logger.error(u'删除教师失败')
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'
