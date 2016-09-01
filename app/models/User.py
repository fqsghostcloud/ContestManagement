# coding=utf-8
import traceback
from flask import current_app
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from app import login_manager


class Permission:
    NORMAL = u'录入信息'
    COLLEGE = u'学院申报'
    DEAN = u'教务处审批'
    SUPER = u'超级用户'

PermissionList = [u'学院申报', u'教务处审批']


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode(128), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(512))
    department = db.Column(db.Unicode(128))
    permission = db.Column(db.Unicode(32), default=Permission.NORMAL)

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return '<User %s>' % (self.username)

    @property
    def password(self):
        raise AttributeError(u'密码不可读')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def level(self):
        for i, key in enumerate(PermissionList, 1):
            if self.permission == key:
                return i

    def save(self):
        db.session.add(self)
        db.session.commit()

    def remove(self):
        db.session.delete(self)
        db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def get_by_id(id):
    return User.query.filter(User.id == id).first()


def get_by_username(username):
    return User.query.filter(User.username == username).first()


def get_list_pageable(page, per_page):
    return User.query.order_by(User.id)\
        .paginate(page, per_page, error_out=False)


def get_count():
    return User.query.count()


def create_user(user_form):
    try:
        has_user = get_by_username(user_form.username.data)
        if has_user:
            current_app.logger.warning(u'用户 %s 已存在', has_user.username)
            return 'REPEAT'
        user = User(user_form.username.data)
        user.password = user_form.password.data
        user.department = user_form.department.data
        user.permission = user_form.permission.data
        user.save()
        current_app.logger.info(u'添加用户 %s 成功', user.username)
        return 'OK'
    except Exception, e:
        current_app.logger.error(u'添加用户 %s 失败', user_form.username.data)
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'


def update_user(user, user_form):
    try:
        user.username = user_form.username.data
        user.password = user_form.password2.data
        user.department = user_form.department.data
        user.permission = user_form.permission.data
        user.save()
        current_app.logger.info(u'更新用户 %s 成功', user.username)
        return 'OK'
    except Exception, e:
        current_app.logger.error(u'更新用户 %s 失败', user_form.username.data)
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'


def delete_by_id(id):
    try:
        user = get_by_id(id)
        user.remove()
        current_app.logger.info(u'删除用户 %d 成功', id)
        return 'OK'
    except Exception, e:
        current_app.logger.error(u'删除用户 %d 失败', id)
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'


def delete_user(user):
    try:
        user.remove()
        current_app.logger.info(u'删除用户成功')
        return 'OK'
    except Exception, e:
        current_app.logger.error(u'删除用户失败')
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'
