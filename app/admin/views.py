# coding=utf-8
import sys
from flask import render_template, redirect, url_for, flash, request, \
    current_app, jsonify
from flask.ext.login import login_required, login_user, logout_user, current_user
from pip._vendor import requests

from . import admin
from .forms import LoginForm, AddUserForm, EditUserForm, ContestSeriesForm, \
    TeacherForm, ContestForm, AwardsForm, StudentForm,ContestLevelForm,AwardsLevelForm,ContestResultForm
from app.models import User, ContestSeries, Teacher, Contest, Awards, Student, \
    Resource,ContestLevel,AwardsLevel,ContestResult
from collections import Counter


@admin.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if request.method == 'POST' and login_form.validate():

        # 此处进行学生身份统一认证
        if login_form.username.data.isdigit() and len(login_form.username.data) == 10:
            user_info = "xh=" + login_form.username.data + "&" + "password=" + login_form.password.data
            r = requests.post("http://bysj.cuit.edu.cn:8098/Interface/TaoRan_Interface.svc/CheckUserPassword",
                              data=user_info)
            r.encoding = 'utf-8'
            s = r.text
            strl = ''
            for x in s[1:]:
                strl += x
            login_status = eval(strl)
            print login_status["code"]
            if login_status["code"] == '1000':
                # login_user(login_status["code"], remember=login_form.remember_me.data)
                user_info1 = "xh=" + login_form.username.data
                j = requests.post("http://bysj.cuit.edu.cn:8098/Interface/TaoRan_Interface.svc/GetUserInfo",
                                  data=user_info1)
                j.encoding = 'utf-8'
                d = j.text

                # 将接受到的字符转化为字符串
                strs = ''
                for x in d[1:]:
                    strs += x

                # 再将字符串字典化
                stu_status = eval(strs)

                # 以下是为了解决子字典转化为字符串后再转化为独立字典时遇到的
                # 错误：UnicodeDecodeError: 'ascii' codec can't decode byte 0xe7 in position 0: ordinal not in range(128)
                reload(sys)
                sys.setdefaultencoding('utf8')
                # 解决结束

                # 字符串化和字典化
                strda = str(stu_status["data"])
                stu_data = eval(strda)

                return render_template('admin/ShowInfo.html',
                                       r=s,
                                       j=stu_status,
                                       f=stu_data)
            else:
                flash(u'用户名或密码错误！')

        # 此处进行管理员的身份数据库验证
        else:
            user = User.get_by_username(login_form.username.data)
            if user is None:
                flash(u'用户不存在')
            elif not user.verify_password(login_form.password.data):
                flash(u'密码错误')
            else:
                login_user(user, remember=login_form.remember_me.data)
                if user.username == 'admin':
                    return redirect(url_for('admin.user'))
                else:
                    return redirect(url_for('admin.contest'))
    return render_template('login.html',
                           login_form=login_form)


@admin.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash(u'你已下线本系统')
    return redirect(url_for('admin.login'))


@admin.route('/')
@admin.route('/index')
@login_required
def index():
    return render_template('admin/base.html')


@admin.route('/user', methods=['GET'])
@login_required
def user():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ADMIN_USER_PER_PAGE']
    if page == -1:
        page = ((User.get_count() - 1) // per_page) + 1
    pagination = User.get_list_pageable(page, per_page)
    user_list = pagination.items
    return render_template('admin/user.html',
                           title = u'超级用户',
                           user_list = user_list,
                           pagination = pagination)


@admin.route('/user/del', methods=['POST'])
@login_required
def user_del():
    user_id = request.form.get('user_id', type=int)
    if current_user.id == user_id:
        ret = u'不能删除本人账号'
    else:
        ret = User.delete_by_id(user_id)
    return jsonify(ret = ret)


@admin.route('/user/add', methods=['GET', 'POST'])
@login_required
def user_add():
    user_form = AddUserForm()
    if request.method == 'POST' and user_form.validate():
        ret = User.create_user(user_form)
        if ret == 'REPEAT':
            flash(u'用户已存在')
        if ret == 'OK':
            return redirect(url_for('admin.user'))
    return render_template('admin/user_form.html',
                           title = u'添加用户', add = True,
                           action = url_for('admin.user_add'),
                           user_form = user_form)


@admin.route('/user/edit/<id>', methods=['GET', 'POST'])
@login_required
def user_edit(id):
    user = User.get_by_id(int(id))
    user_form = EditUserForm()
    if request.method == 'GET':
        user_form.username.data = user.username
        user_form.department.data = user.department
        user_form.permission.data = user.permission
    if request.method == 'POST' and user_form.validate():
        ret = User.update_user(user, user_form)
        if ret == 'OK':
            return redirect(url_for('admin.user'))
    return render_template('admin/user_form.html',
                           title = u'修改用户',
                           action = url_for('admin.user_edit', id = id),
                           user_form = user_form)

#
#竞赛等级
#
@admin.route('/contest_level', methods=['GET'])
@login_required
def contest_level():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ADMIN_CONTESTLEVEL_PER_PAGE']
    if page == -1:
        page = ((ContestLevel.get_count() - 1) // per_page) + 1
    pagination = ContestLevel.get_list_pageable(page, per_page)
    level_list = pagination.items
    count = ContestLevel.get_count()
    list = []
    for i in range(count):
        list.append(int(i + 1))
    return render_template('admin/contest_level.html',
                           title = u'竞赛等级管理',
                           level_list = level_list,
                           list = list,
                           pagination = pagination,
                           count = count)

@admin.route('/contest_level1/<test>/<cid>', methods=['GET'])
@login_required
def contest_level1(test,cid):
    if int(test) == int(1):
        ContestLevel.get_new_list(int(test),int(cid))
    if int(test) == int(2):
        ContestLevel.get_new_list(int(test),int(cid))
    return redirect(url_for('admin.contest_level'))

@admin.route('/contest_level/add', methods=['GET', 'POST'])
@login_required
def contest_level_add():
    level_form = ContestLevelForm()
    if request.method == 'POST' and level_form.validate():
        ret = ContestLevel.create_level(level_form)
        if ret == 'OK':
            return redirect(url_for('admin.contest_level'))
        elif ret == 'FAIL':
            flash(u'提交失败')
        else:
            flash(ret)
    return render_template('admin/contest_level_form.html',
                           title = u'竞赛等级录入',
                           action = url_for('admin.contest_level_add'),
                           level_form = level_form)

@admin.route('/contest_level/del', methods=['POST'])
@login_required
def contest_level_del():
    level_id = request.form.get('contest_level_id', -1, type=int)
    if level_id != -1:
        level = ContestLevel.get_by_id(level_id)
        ret = ContestLevel.delete_level(level)
    else:
        ret = u'删除失败'
    return jsonify(ret = ret)

@admin.route('/contest_level/edit/<id>', methods=['GET', 'POST'])
@login_required
def contest_level_edit(id):
    level = ContestLevel.get_by_id(id)
    level_form = ContestLevelForm()
    if request.method == 'GET':
        level_form.name.data = level.name
        level_form.budget_text.data = level.budget_text
    if request.method == 'POST' and level_form.validate():
        ret = ContestLevel.update_level(level,level_form)
        if ret == 'OK':
            return redirect(url_for('admin.contest_level'))
        elif ret == 'FAIL':
            flash(u'提交失败')
        else:
            flash(ret)
    return render_template('admin/contest_level_form.html',
                           title = u'竞赛等级修改',
                           action = url_for('admin.contest_level_edit', id=id),
                           level_form = level_form)
#
#奖项等级
#
@admin.route('/awards_level', methods=['GET'])
@login_required
def awards_level():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ADMIN_AWARDSLEVEL_PER_PAGE']
    if page == -1:
        page = ((AwardsLevel.get_count() - 1) // per_page) + 1
    pagination = AwardsLevel.get_list_pageable(page, per_page)
    awards_list = pagination.items
    count = AwardsLevel.get_count()
    list = []
    for i in range(count):
        list.append(int(i + 1))
    return render_template('admin/awards_level.html',
                           title = u'奖项等级管理',
                           list = list,
                           awards_list = awards_list,
                           pagination = pagination,
                           count = count)

@admin.route('/awards_level1/<test>/<cid>', methods=['GET'])
@login_required
def awards_level1(test,cid):
    if int(test) == int(1):
        AwardsLevel.get_new_list(int(test),int(cid))
    if int(test) == int(2):
        AwardsLevel.get_new_list(int(test),int(cid))
    return redirect(url_for('admin.awards_level'))

@admin.route('/awards_level/add', methods=['GET', 'POST'])
@login_required
def awards_level_add():
    awards_form = AwardsLevelForm()
    if request.method == 'POST' and awards_form.validate():
        ret = AwardsLevel.create_level(awards_form)
        if ret == 'OK':
            return redirect(url_for('admin.awards_level'))
        elif ret == 'FAIL':
            flash(u'提交失败')
        else:
            flash(ret)
    return render_template('admin/awards_level_form.html',
                           title = u'竞赛等级录入',
                           action = url_for('admin.awards_level_add'),
                           awards_form = awards_form)

@admin.route('/awards_level/del', methods=['POST'])
@login_required
def awards_level_del():
    level_id = request.form.get('awards_level_id', -1, type=int)
    if level_id != -1:
        level = AwardsLevel.get_by_id(level_id)
        ret = AwardsLevel.delete_level(level)
    else:
        ret = u'删除失败'
    return jsonify(ret = ret)

@admin.route('/awards_level/edit/<id>', methods=['GET', 'POST'])
@login_required
def awards_level_edit(id):
    level = AwardsLevel.get_by_id(id)
    level_form = AwardsLevelForm()
    if request.method == 'GET':
        level_form.name.data = level.name
        level_form.budget_text.data = level.budget_text
    if request.method == 'POST' and level_form.validate():
        ret = AwardsLevel.update_level(level,level_form)
        if ret == 'OK':
            return redirect(url_for('admin.awards_level'))
        elif ret == 'FAIL':
            flash(u'提交失败')
        else:
            flash(ret)
    return render_template('admin/awards_level_form.html',
                           title = u'竞赛等级修改',
                           action = url_for('admin.awards_level_edit', id=id),
                           awards_form = level_form)

#
#竞赛档次
#

@admin.route('/result', methods=['GET'])
@login_required
def result():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ADMIN_RESULT_PER_PAGE']
    if page == -1:
         page = ((ContestResult.get_count() - 1) // per_page) + 1
    pagination = ContestResult.get_list_pageable(page, per_page)
    result_list = pagination.items
    count = ContestResult.get_count()
    list = []
    for i in range(count):
        list.append(int(i + 1))
    return render_template('admin/result.html',
                           title = u'竞赛档次管理',
                           result_list = result_list,
                           list = list,
                           pagination = pagination,
                           count = count)

@admin.route('/result1/<test>/<cid>', methods=['GET'])
@login_required
def result1(test,cid):
    if int(test) == int(1):
        ContestResult.get_new_list(int(test),int(cid))
    if int(test) == int(2):
        ContestResult.get_new_list(int(test),int(cid))
    return redirect(url_for('admin.result'))

@admin.route('/result/del', methods=['POST'])
@login_required
def result_del():
    result_id = request.form.get('result_id', -1, type=int)
    if result_id != -1:
        result = ContestResult.get_by_id(result_id)
        ret = ContestResult.delete_result(result)
    else:
        ret = result_id
        ret = u'删除失败'
    return jsonify(ret = ret)


@admin.route('/result/add', methods=['GET', 'POST'])
@login_required
def result_add():
    result_form = ContestResultForm()
    if request.method == 'POST' and result_form.validate():
        ret = ContestResult.create_result(result_form)
        if ret == 'OK':
            return redirect(url_for('admin.result'))
        elif ret == 'FAIL':
            flash(u'提交失败')
        else:
            flash(ret)
    return render_template('admin/result_form.html',
                           title = u'竞赛档次录入',
                           action = url_for('admin.result_add'),
                           result_form = result_form)


@admin.route('/result/edit/<id>', methods=['GET', 'POST'])
@login_required
def result_edit(id):
    result = ContestResult.get_by_id(id)
    result_form = ContestResultForm()
    if request.method == 'GET':
        result_form.name.data = result.name
        result_form.budget_text.data = result.budget_text
    if request.method == 'POST' and result_form.validate():
        ret = ContestResult.update_result(result, result_form)
        if ret == 'OK':
            return redirect(url_for('admin.result'))
        elif ret == 'FAIL':
            flash(u'提交失败')
        else:
            flash(ret)
    return render_template('admin/result_form.html',
                           title = u'竞赛档次修改',
                           action = url_for('admin.result_edit', id=id),
                           result_form = result_form)
#
#竞赛系列
#
@admin.route('/series', methods=['GET'])
@login_required
def series():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ADMIN_SERIES_PER_PAGE']
    if page == -1:
        page = ((ContestSeries.get_count() - 1) // per_page) + 1
    pagination = ContestSeries.get_list_pageable(page, per_page)
    series_list = pagination.items
    return render_template('admin/series.html',
                           title = u'竞赛系列管理',
                           series_list = series_list,
                           pagination = pagination)


@admin.route('/series/del', methods=['POST'])
@login_required
def series_del():
    series_id = request.form.get('series_id', -1, type=int)
    if series_id != -1:
        series = ContestSeries.get_by_id(series_id)
        ret = ContestSeries.delete_series(series)
    else:
        ret = u'删除失败'
    return jsonify(ret = ret)


@admin.route('/series/add', methods=['GET', 'POST'])
@login_required
def series_add():
    series_form = ContestSeriesForm()
    if request.method == 'POST' and series_form.validate():
        ret = ContestSeries.create_series(series_form)
        if ret == 'OK':
            return redirect(url_for('admin.series'))
        elif ret == 'FAIL':
            flash(u'提交失败')
        else:
            flash(ret)
    return render_template('admin/series_form.html',
                           title = u'竞赛系列录入',
                           action = url_for('admin.series_add'),
                           series_form = series_form)


@admin.route('/series/edit/<id>', methods=['GET', 'POST'])
@login_required
def series_edit(id):
    series = ContestSeries.get_by_id(id)
    series_form = ContestSeriesForm()
    if request.method == 'GET':
        series_form.name.data = series.name
        series_form.budget_text.data = series.budget_text
    if request.method == 'POST' and series_form.validate():
        ret = ContestSeries.update_series(series, series_form)
        if ret == 'OK':
            return redirect(url_for('admin.series'))
        elif ret == 'FAIL':
            flash(u'提交失败')
        else:
            flash(ret)
    return render_template('admin/series_form.html',
                           title = u'竞赛系列修改',
                           action = url_for('admin.series_edit', id=id),
                           series_form = series_form)


@admin.route('/student', methods=['GET', 'POST'])
@login_required
def student():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ADMIN_STUDENT_PER_PAGE']
    if page == -1:
        page = ((Student.get_count() - 1) // per_page) + 1
    pagination = Student.get_list_pageable(page, per_page)
    student_list = pagination.items
    return render_template('admin/student.html',
                           title = u'学生管理',
                           student_list = student_list,
                           pagination = pagination)


@admin.route('/student/del', methods=['POST'])
@login_required
def student_del():
    student_id = request.form.get('student_id', -1, type=int)
    if student_id != -1:
        student = Student.get_by_id(student_id)
        ret = Student.delete_student(student)
    else:
        ret = u'删除失败'
    return jsonify(ret = ret)


@admin.route('/student/add', methods=['GET', 'POST'])
@login_required
def student_add():
    student_form = StudentForm()
    if request.method == 'POST' and student_form.validate():
        ret = Student.create_student(student_form)
        if ret == 'OK':
            return redirect(url_for('admin.student'))
        elif ret == 'FAIL':
            flash(u'提交失败')
        else:
            flash(ret)
    return render_template('admin/student_form.html',
                           title = u'添加学生',
                           action = url_for('admin.student_add'),
                           student_form = student_form)


@admin.route('/student/edit/<id>', methods=['GET', 'POST'])
@login_required
def student_edit(id):
    student = Student.get_by_id(id)
    student_form = StudentForm()
    if request.method == 'GET':
        student_form.stu_no.data = student.stu_no
        student_form.name.data = student.name
        student_form.department.data = student.department
        student_form.major.data = student.major
        student_form.grade.data = student.grade
    if request.method == 'POST' and student_form.validate():
        ret = Student.update_student(student, student_form)
        if ret == 'OK':
            return redirect(url_for('admin.student'))
        elif ret == 'FAIL':
            flash(u'提交失败')
        else:
            flash(ret)
    return render_template('admin/student_form.html',
                           title = u'修改学生',
                           action = url_for('admin.student_edit', id=id),
                           student_form = student_form)


@admin.route('/teacher', methods=['GET', 'POST'])
@login_required
def teacher():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ADMIN_TEACHER_PER_PAGE']
    if page == -1:
        page = ((Teacher.get_count() - 1) // per_page) + 1
    pagination = Teacher.get_list_pageable(page, per_page)
    teacher_list = pagination.items
    return render_template('admin/teacher.html',
                           title = u'教师管理',
                           teacher_list = teacher_list,
                           pagination = pagination)


@admin.route('/teacher/del', methods=['POST'])
@login_required
def teacher_del():
    teacher_id = request.form.get('teacher_id', -1, type=int)
    if teacher_id != -1:
        teacher = Teacher.get_by_id(teacher_id)
        ret = Teacher.delete_teacher(teacher)
    else:
        ret = u'删除失败'
    return jsonify(ret = ret)


@admin.route('/teacher/add', methods=['GET', 'POST'])
@login_required
def teacher_add():
    teacher_form = TeacherForm()
    if request.method == 'POST' and teacher_form.validate():
        ret = Teacher.create_teacher(teacher_form)
        if ret == 'OK':
            return redirect(url_for('admin.teacher'))
        elif ret == 'FAIL':
            flash(u'提交失败')
        else:
            flash(ret)
    return render_template('admin/teacher_form.html',
                           title = u'添加教师',
                           action = url_for('admin.teacher_add'),
                           teacher_form = teacher_form)


@admin.route('/teacher/edit/<id>', methods=['GET', 'POST'])
@login_required
def teacher_edit(id):
    teacher = Teacher.get_by_id(id)
    teacher_form = TeacherForm()
    if request.method == 'GET':
        teacher_form.name.data = teacher.name
        teacher_form.department.data = teacher.department
    if request.method == 'POST' and teacher_form.validate():
        ret = Teacher.update_teacher(teacher, teacher_form)
        if ret == 'OK':
            return redirect(url_for('admin.teacher'))
        elif ret == 'FAIL':
            flash(u'提交失败')
        else:
            flash(ret)
    return render_template('admin/teacher_form.html',
                           title = u'修改教师',
                           action = url_for('admin.teacher_edit', id=id),
                           teacher_form = teacher_form)


@admin.route('/contest', methods=['GET', 'POST'])
@login_required
def contest():
    page = request.args.get('page', 1, type=int)
    filter_pass = request.args.get('filter_pass', 0, type=int)
    per_page = current_app.config['ADMIN_CONTEST_PER_PAGE']
    department = current_user.department if current_user.department != u'教务处' else None
    if page == -1:
        page = ((Contest.get_count(filter_pass, department) - 1) // per_page) + 1
    pagination = Contest.get_list_pageable(page, per_page, filter_pass,
                                           department)
    contest_list = pagination.items
    return render_template('admin/contest.html',
                           title = u'竞赛管理',
                           contest_list = contest_list,
                           pagination = pagination,
                           filter_pass = filter_pass,
                           department = department)
#
#通过申请编辑
#
@admin.route('/contest/<id>', methods=['GET', 'POST'])
@login_required
def contest_apply_through(id):
    contest = Contest.get_by_id(id)
    if contest.apply == u'2':
        contest.apply = 3
    elif contest.apply == u'4':
        contest.apply = 1
    contest.save()
    page = request.args.get('page', 1, type=int)
    filter_pass = request.args.get('filter_pass', 0, type=int)
    per_page = current_app.config['ADMIN_CONTEST_PER_PAGE']
    department = current_user.department if current_user.department != u'教务处' else None
    if page == -1:
        page = ((Contest.get_count(filter_pass, department) - 1) // per_page) + 1
    pagination = Contest.get_list_pageable(page, per_page, filter_pass,
                                           department)
    contest_list = pagination.items
    return render_template('admin/contest.html',
                           title = u'竞赛管理',
                           contest_list = contest_list,
                           pagination = pagination,
                           filter_pass = filter_pass,
                           department = department)
#
#拒绝申请
#
@admin.route('/contest_refuse/<id>', methods=['GET', 'POST'])
@login_required
def contest_apply_refuse(id):
    contest = Contest.get_by_id(id)
    if contest.apply == u'2':
        contest.apply = 1
    elif contest.apply == u'4':
        contest.apply = 3
    contest.save()
    page = request.args.get('page', 1, type=int)
    filter_pass = request.args.get('filter_pass', 0, type=int)
    per_page = current_app.config['ADMIN_CONTEST_PER_PAGE']
    department = current_user.department if current_user.department != u'教务处' else None
    if page == -1:
        page = ((Contest.get_count(filter_pass, department) - 1) // per_page) + 1
    pagination = Contest.get_list_pageable(page, per_page, filter_pass,
                                           department)
    contest_list = pagination.items
    return render_template('admin/contest.html',
                           title = u'竞赛管理',
                           contest_list = contest_list,
                           pagination = pagination,
                           filter_pass = filter_pass,
                           department = department)

@admin.route('/contest/del', methods=['POST'])
@login_required
def contest_del():
    contest_id = request.form.get('contest_id', -1, type=int)
    if contest_id != -1:
        contest = Contest.get_by_id(contest_id)
        ret = Contest.delete_contest(contest)
    else:
        ret = u'删除失败'

    return jsonify(ret = ret)


@admin.route('/contest/add', methods=['GET', 'POST'])
@login_required
def contest_add():
    contest_form = ContestForm()
    contest_form.department.data = current_user.department
    if request.method == 'POST' and contest_form.validate():
        ret = Contest.create_contest(contest_form, request)
        if ret == 'OK':
            return redirect(url_for('admin.contest'))
        elif ret == 'FAIL':
            flash(u'提交失败')
        else:
            flash(ret)
    current_app.logger.error(contest_form.errors)
    return render_template('admin/contest_form.html',
                           title = u'添加竞赛',
                           action = url_for('admin.contest_add'),
                           contest_form = contest_form)

@admin.route('/contest/apply/<id>', methods=['GET', 'POST'])
@login_required
def contest_apply(id):
    contest = Contest.get_by_id(id)
    contest.apply = 2
    contest.save()
    page = request.args.get('page', 1, type=int)
    filter_pass = request.args.get('filter_pass', 0, type=int)
    per_page = current_app.config['ADMIN_CONTEST_PER_PAGE']
    department = current_user.department if current_user.department != u'教务处' else None
    if page == -1:
        page = ((Contest.get_count(filter_pass, department) - 1) // per_page) + 1
    pagination = Contest.get_list_pageable(page, per_page, filter_pass,
                                           department)
    contest_list = pagination.items
    return render_template('admin/contest.html',
                           title = u'竞赛管理',
                           contest_list = contest_list,
                           pagination = pagination,
                           filter_pass = filter_pass,
                           department = department)
#
#申请编辑
#


@admin.route('/contest/edit/<id>', methods=['GET', 'POST'])
@login_required
def contest_edit(id):
    contest = Contest.get_by_id(id)
    contest_form = ContestForm()
    contest_form.department.data = current_user.department
    if request.method == 'GET':
        contest_form.name_cn.data = contest.name_cn
        contest_form.name_en.data = contest.name_en
        #contest_form.level_id.data = contest.level
        contest_form.type.data = contest.type
        contest_form.department.data = contest.department
        contest_form.site.data = contest.site
        contest_form.organizer.data = contest.organizer
        contest_form.co_organizer.data = contest.co_organizer
        contest_form.place.data = contest.place
        if contest.series:
            contest_form.series_id.data = contest.series.id
        if contest.level_name:
            contest_form.level_id.data = contest.level.id
        # contest_form.year.data = contest.year
        contest_form.date_range.data = [contest.start_date.strftime('%Y/%m/%d'),
                                        contest.end_date.strftime('%Y/%m/%d')]
        contest_form.budget.data = contest.budget
        contest_form.budget_text.data = contest.budget_text
        contest_form.student_num.data = contest.student_num
        contest_form.teacher_num.data = contest.teacher_num
        # contest_form.subject.data = contest.subject
    if request.method == 'POST' and contest_form.validate():
        ret = Contest.update_contest(contest, contest_form, request)
        if ret == 'OK':
            if contest.apply == u'3':
                contest.apply = 4
            contest.save()
            return redirect(url_for('admin.contest'))
        elif ret == 'FAIL':
            flash(u'提交失败')
        else:
            flash(ret)
        print ret
    current_app.logger.error(contest_form.errors)
    return render_template('admin/contest_form.html',
                           title = u'修改竞赛',
                           action = url_for('admin.contest_edit', id=id),
                           contest_form = contest_form)


@admin.route('/contest/check/<id>', methods=['GET', 'POST'])
@login_required
def contest_check(id):
    contest = Contest.get_by_id(id)
    contests = Contest.ResultList()
    contestResult = ContestResult.get_all()
    if request.method == 'POST':
        result = request.form.get('result', 0, type=int)
        current_app.logger.info(result)
        contest.result = contests[result-1].name
        if contest.apply == u'0':
            contest.apply = 1
        contest.save()
    return render_template('admin/contest_check.html',
                           title = u'审核竞赛',
                           contest = contest,
                           contestResult = contestResult)

#
#竞赛查看
#
@admin.route('/contest/see/<id>', methods=['GET', 'POST'])
@login_required
def contest_see(id):
    contest = Contest.get_by_id(id)
    contests = Contest.ResultList()
    contestResult = contests[0:]
    if request.method == 'POST':
        result = request.form.get('result', 0, type=int)
        current_app.logger.info(result)
        contest.result = contests[result-1].name
        contest.save()
    return render_template('admin/contest_see.html',
                           title = u'竞赛查看',
                           contest = contest,
                           contestResult = contestResult)

@admin.route('/contest_plan/config_print')
@login_required
def contest_plan_config_print():
    from datetime import date
    year_now = date.today().year
    cur_year = request.args.get('year', year_now, type=int) #获取连接里面的参数的值。year的值
    year_select = Contest.get_year()
    # year_select = [year for year in range(cur_year - 2, cur_year + 1)]
    department = current_user.department if current_user.department != u'教务处' else None
    contest_list = Contest.get_list_pageable(page=-1, department=department)
    return render_template('admin/contest_plan_config_print.html',
                           title = u'打印竞赛计划表',
                           department = department,
                           contest_list = contest_list,
                           year_select = year_select,
                           cur_year =cur_year,
                           int = int)


@admin.route('/pre_award', methods=['GET'])
@login_required
def pre_award():
    page = request.args.get('page', 1, type=int)
    filter_pass = request.args.get('filter_pass', 0, type=int)
    per_page = current_app.config['ADMIN_CONTEST_PER_PAGE']
    department = current_user.department if current_user.department != u'教务处' else None
    if page == -1:
        page = ((Contest.get_count(filter_pass, department) - 1) // per_page) + 1
    pagination = Contest.get_list_pageable(page, per_page, filter_pass,
                                           department)
    contest_list = pagination.items
    return render_template('admin/pre_award.html',
                           title = u'竞赛管理',
                           contest_list = contest_list,
                           pagination = pagination,
                           filter_pass = filter_pass,
                           department = department)


@admin.route('/awards/<id>', methods=['GET'])
@login_required
def awards(id):
    contest = Contest.get_by_id(id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ADMIN_AWARDS_PER_PAGE']
    department = current_user.department if current_user.department != u'教务处' else None
    if page == -1:
        page = ((Awards.get_count(contest_id=contest.contest_id) - 1) // per_page) + 1
    pagination = Awards.get_list_pageable(page, per_page,
                                          contest_id=contest.contest_id)
    awards_list = pagination.items
    return render_template('admin/awards.html',
                           title = u'奖项管理',
                           contest = contest,
                           awards_list = awards_list,
                           pagination = pagination,
                           process = Awards.AwardsProcess,
                           department = department)
#
#查看奖项
#


@admin.route('/awards/del', methods=['POST'])
@login_required
def awards_del():
    awards_id = request.form.get('awards_id', -1)
    if awards_id != -1:
        awards = Awards.get_by_id(awards_id)
        ret = Awards.delete_awards(awards)
    else:
        ret = u'删除失败'
    return jsonify(ret = ret)


@admin.route('/contest/<id>/awards/add', methods=['GET', 'POST'])
@login_required
def awards_add(id):
    contest = Contest.get_by_id(id)
    awards_form = AwardsForm()
    i =0
    awards_form.department.data = current_user.department
    # cid = contest.contest_id
    # Awards.set_new_apply(cid)
    request.values.get('StudentList')
    if request.method == 'POST' and awards_form.validate():
        ret = Awards.create_awards(awards_form, contest, request.files)
        if ret == 'OK':
            return redirect(url_for('admin.awards', id=contest.id))
        elif ret == 'FAIL':
            flash(u'提交失败')
        else:
            flash(ret)
    return render_template('admin/awards_form.html',
                           title = u'奖项录入',
                           contest = contest,
                           awards_form = awards_form,
                           i=i
                           )


@admin.route('/contest/<id>/awards/edit/<awards_id>', methods=['GET', 'POST'])
@login_required
def awards_edit(id, awards_id):
    contest = Contest.get_by_id(id)
    awards = Awards.get_by_id(awards_id)
    exist_resources = awards.resources
    awards_form = AwardsForm()
    # if awards.apply == 3 or awards.apply == 5:
    #     cid = contest.contest_id
    #     Awards.set_all_apply_to_zero(cid)
    i = 1
    if request.method == 'GET':
        awards_form.honor.data = awards.honor
        awards_form.level.data = awards.level
        awards_form.title.data = awards.title
        awards_form.type.data = awards.type
        # if awards.teachers:
        #     teacher = awards.teachers[0]
        #     awards_form.teachers.data = teacher.name
        awards_form.teachers.data = [t.name for t in awards.teachers]
        awards_form.students.data = [s.stu_no for s in awards.students]
    if request.method == 'POST' and awards_form.validate():
        ret = Awards.update_awards(awards, awards_form, request.files)
        if ret == 'OK':
            return redirect(url_for('admin.awards', id=contest.id))
        elif ret == 'FAIL':
            flash(u'提交失败')
        else:
            flash(ret)
    return render_template('admin/awards_form.html',
                           title = u'奖项修改',
                           contest = contest,
                           awards_form = awards_form,
                           exist_resources = exist_resources,
                           awards = awards,
                           i = i)
#
#奖项查看
#
@admin.route('/contest/<id>/awards/check/<awards_id>', methods=['GET', 'POST'])
@login_required
def awards_check(id, awards_id):
    contest = Contest.get_by_id(id)
    awards = Awards.get_by_id(awards_id)
    exist_resources = awards.resources
    awards_form = AwardsForm()
    department = current_user.department if current_user.department != u'教务处' else None
    if request.method == 'GET':
        awards_form.honor.data = awards.honor
        awards_form.level.data = awards.level
        awards_form.title.data = awards.title
        awards_form.type.data = awards.type
        if awards.teachers:
            teacher = awards.teachers[0]
            awards_form.teachers.data = teacher.name
        awards_form.students.data = [s.stu_no for s in awards.students]
    if request.method == 'POST' and awards_form.validate():
        ret = Awards.update_awards(awards, awards_form, request.files)
        if ret == 'OK':
            return redirect(url_for('admin.awards', id=contest.id))
        elif ret == 'FAIL':
            flash(u'提交失败')
        else:
            flash(ret)
    return render_template('admin/awards_form_check.html',
                           title = u'奖项查看',
                           contest = contest,
                           awards_form = awards_form,
                           awards = awards,
                           exist_resources = exist_resources,
                           department = department)

#
#通过审核查看奖项
#
@admin.route('/contest/<id>/awards/after/check/<awards_id>', methods=['GET', 'POST'])
@login_required
def awards_check_after_pass(id, awards_id):
    contest = Contest.get_by_id(id)
    awards = Awards.get_by_id(awards_id)
    exist_resources = awards.resources
    return render_template('admin/awards_see.html',
                           title = u'奖项查看1',
                           contest = contest,
                           awards = awards,
                           exist_resources = exist_resources,
                           )

#
#竞赛所有奖项审核通过
#
@admin.route('/contest/<id>/awards_pass',methods=['GET','POST'])
@login_required
def awards_pass_check(id):
    contest = Contest.get_by_id(id)
    cid = contest.contest_id
    Awards.set_all_apply(cid)
    return redirect(url_for('admin.awards',id = id))
#
#竞赛奖项审核不通过
#
@admin.route('/contest/<id>/awards_required_refuse',methods=['GET','POST'])
@login_required
def awards_refuse_check(id):
    contest = Contest.get_by_id(id)
    cid = contest.contest_id
    Awards.set_all_apply_refuse(cid)
    return  redirect(url_for('admin.awards',id = id))
#
#申请编辑奖项
#
@admin.route('/contest/<cid>awards_required_edit/<id>',methods=['GET','POST'])
@login_required
def awards_require_edit(cid,id):
    # contest = Contest.get_by_id(id)
    # cid = contest.contest_id
    awards = Awards.get_by_id(id)
    awards.apply = int(3)
    awards.process = u'申请待审核'
    return redirect(url_for('admin.awards',id = cid))
#
#申请编辑审核通过
#
@admin.route('/contest/<cid>awards_required_through/<id>',methods=['GET','POST'])
@login_required
def awards_required_through(cid,id):
    # contest = Contest.get_by_id(id)
    # cid = contest.contest_id
    awards = Awards.get_by_id(id)
    awards.apply = int(4)
    awards.process = u'已审核'
    return redirect(url_for('admin.awards',id = cid))

#
#申请编辑审核不通过
#
@admin.route('/contest/<cid>awards_required_refuse/<id>',methods=['GET','POST'])
@login_required
def awards_required_refuse(cid,id):
    # contest = Contest.get_by_id(id)
    # cid = contest.contest_id
    awards = Awards.get_by_id(id)
    awards.apply = int(5)
    awards.process = u'申请不通过'
    return redirect(url_for('admin.awards',id = cid))
#
#奖项审核
#
@admin.route('/contest/<id>/awards_pass/<awards_id>', methods=['GET', 'POST'])
@login_required
def awards_check_pass(id,awards_id):
    awards = Awards.get_by_id(awards_id)
    awards.apply = 1        #apply表示已审核
    awards.process = u'已审核'
    awards.save()
    return redirect(url_for('admin.awards',id = id))


@admin.route('/contest/<id>/awards_refuse/<awards_id>', methods=['GET', 'POST'])
@login_required
def awards_check_refuse(id,awards_id):
    awards = Awards.get_by_id(awards_id)
    awards.apply = 2        #apply表示审核不通过
    awards.process = u'审核不通过'
    awards.save()
    return redirect(url_for('admin.awards',id = id))

@admin.route('/resource/del', methods=['POST'])
@login_required
def resource_del():
    res_id = request.form.get('res_id', -1)
    if res_id != -1:
        res = Resource.get_by_id(res_id)
        ret = Resource.delete_res(res)
    else:
        ret = u'删除失败'
    return jsonify(ret = ret)

@admin.route('/stu/Find', methods = ['POST'])
@login_required
def stu_Find():
    stu_id = request.form.get('stu_id', -1)
    if stu_id != -1:
        stu = Student.get_by_stu_no(stu_id)
        current_app.logger.info(stu)
        if stu is None:
            ret = 'FAIL'
        else:
            ret = 'OK'
    else:
        ret = 'FAIL'
    return jsonify(ret = ret)


@admin.route('/tea/Find', methods = ['POST'])
@login_required
def tea_Find():
    tea_name = request.form.get('tea_name', -1)
    if tea_name != -1:
        tea = Teacher.get_by_name(tea_name)
        if tea is None:
            ret = 'FAIL'
        else:
            ret = 'OK'
    else:
        ret = 'FAIL'
    return jsonify(ret = ret)

@admin.route('/teachers.json', methods=['GET'])
@login_required
def teachers_json():
    query = request.args.get('query', None)
    teachers = Teacher.get_all(query)
    return jsonify(teachers = [t.to_json() for t in teachers])

@admin.route('/students.json', methods=['GET'])
@login_required
def students_json():
    query = request.args.get('query', None)
    students = Student.get_all_list(query)
    return jsonify(students = [t.to_json() for t in students])

@admin.route('/print/contest/<id>', methods=['GET'])
@login_required
def contest_print(id):
    contest = Contest.get_by_id(id)
    return render_template('print/contest.html',
                           contest = contest)


@admin.route('/print/contest_plan', methods=['GET'])
@login_required
def contest_plan_print():
    year = request.args.get('year', 0, type=int)
    department = current_user.department if current_user.department != u'教务处' else None
    contest_list = Contest.get_list_pageable(page=-1, department=department, year=year)
    return render_template('print/contest_plan.html',
                           contest_list = contest_list,
                           department = department.replace(u'学院', ''),
                           year = year,
                           len = len)

@admin.route('/statistics/',methods=['GET'])
@login_required
def statistics():
    all_contest = Contest.get_alls()
    j = 0
    department = []
    for next_contest in all_contest:
        department.append(all_contest[j].department)
        j = j + 1
    counter = Counter(department)
    all_awards = Awards.get_all()
    i = 0
    level = []
    for next_awards in all_awards:
        level.append(all_awards[i].level)
        i = i + 1
    levels = Counter(level)
    return render_template('admin/statistics.html',
                           title = u'统计',
                           counter = counter,
                           level = levels
                           )

@admin.route('/statistics_form/',methods=['GET'])
@login_required
def statistics_form():
    all_contest = Contest.get_alls()
    j = 0
    department = []
    for next_contest in all_contest:
        department.append(all_contest[j].department)
        j = j + 1
    counter = Counter(department)
    all_awards = Awards.get_all()
    i = 0
    level = []
    for next_awards in all_awards:
        level.append(all_awards[i].level)
        i = i + 1
    levels = Counter(level)
    return render_template('admin/statisticsform.html',
                           title = u'统计',
                           counter = counter,
                           level = levels
                           )

@admin.route('/statistics_form_1/',methods=['GET'])
@login_required
def statistics_form_1():
    filter_pass = request.args.get('filter_pass', -1, type=int)
    list = [u'球',u'国家',u'省',u'市',u'校']
    from datetime import date
    year_now = date.today().year
    year_select = [str(year) for year in range(year_now-4,year_now+1)]
    awards_level = Awards.get_level_by_level()
    level_list = []
    number = []
    for l in list:
        for a in awards_level:
            if l in a and not l in level_list:
                level_list.append(l)
    if filter_pass != -1:
        level_selected = level_list[filter_pass]
    else:
        level_selected = u'所有'
        for l in level_list:
            n = 0
            for a in awards_level:
                if l in a:
                    n = n + 1
            number.append(n)
    awards_num = Awards.get_awards_num(level_selected)
    list_len = len(awards_num) / 5

    return render_template('admin/statisticsform1.html',
                           title = u'统计',
                           filter_pass = filter_pass,
                           list = list,
                           year_select = year_select,
                           awards_level = awards_level,
                           awards_num = awards_num,
                           level_list = level_list,
                           list_len = list_len,
                           number = number
                           )


@admin.route('/statistics_form_2/',methods=['GET','POST'])
@login_required
def statistics_form_2():
    filter_pass = request.args.get('filter_pass', 0, type=int)
    print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
    print filter_pass
    list = [u'球',u'国家',u'省',u'市',u'校']
    from datetime import date
    year_now = date.today().year
    year_select = [str(year) for year in range(year_now-4,year_now+1)]
    cur_year = request.args.get('year', year_now, type=int) #获取连接里面的参数的值。year的值
    print "#####################"
    print cur_year
    awards_level = Awards.get_level_by_level()
    # 得到国家级省级...
    level_list = []
    number = []
    for l in list:
        for a in awards_level:
            if l in a and not l in level_list:
                level_list.append(l)

    if filter_pass != -1:
        level_selected = level_list[filter_pass]
    else:
        level_selected = u'所有'
        for l in level_list:
            n = 0
            for a in awards_level:
                if l in a:
                    n = n + 1
            number.append(n)
    print level_selected
    print cur_year
    awards_num = Awards.get_awards_num2(cur_year,level_selected)
    department = []
    ad = Awards.get_all()
    for d in ad:
        if not d.department in department:
            department.append(d.department)
    list_len = len(awards_num) / len(department)
    print awards_num
    return render_template('admin/statisticsform2.html',
                           title = u'统计',
                           filter_pass = filter_pass,
                           list = list,
                           year_select = year_select,
                           awards_level = awards_level,
                           awards_num = awards_num,
                           level_list = level_list,
                           list_len = list_len,
                           cur_year = cur_year,
                           department = department,
                           number = number
                           )