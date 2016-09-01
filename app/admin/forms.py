# coding=utf-8
from datetime import date
from flask.ext.wtf import Form
from wtforms import Field, StringField, PasswordField, BooleanField,\
    SubmitField, SelectField, RadioField, SelectMultipleField, FileField, \
    FloatField, TextAreaField, IntegerField
from wtforms.validators import Length, Optional, EqualTo, ValidationError,DataRequired
from ..utils.validators import MyDataRequired,MyDataRequired1
from wtforms.widgets import TextInput
from app import DepartmentList
from app.models import User, Contest, ContestSeries, Awards, Student, Teacher,ContestLevel


class LoginForm(Form):
    username = StringField(u'用户名', validators=[MyDataRequired(), Length(2, 64, message=u'用户名长度在2到64之间')])
    password = PasswordField(u'密码', validators=[MyDataRequired()])
    remember_me = BooleanField(u'记住我')
    submit = SubmitField(u'登录')

class AddUserForm(Form):
    username = StringField(u'用户名', validators=[MyDataRequired(), Length(2, 64, message=u'用户名长度在2到64之间')])
    password = PasswordField(u'密码', validators=[MyDataRequired()])
    department = SelectField(u'部门', validators=[MyDataRequired()], default="-1")
    permission = RadioField(u'权限', choices=[(permission, permission) for permission in User.PermissionList],
    default=User.Permission.COLLEGE)

    def __init__(self, *args, **kwargs):
        super(AddUserForm, self).__init__(*args, **kwargs)
        self.department.choices = [("-1", u"--- 请选择 ---")] + [(department, department) for department in DepartmentList]

    def validate_department(form, field):
        if field.data == "-1":
            raise ValidationError(u'请下拉选择一个选项')


class EditUserForm(Form):
    username = StringField(u'用户名', validators=[MyDataRequired(), Length(2, 64, message=u'用户名长度在2到64之间')])
    password = PasswordField(u'原密码', validators=[MyDataRequired()])
    password2 = PasswordField(u'新密码', validators=[MyDataRequired()])
    department = SelectField(u'部门', validators=[MyDataRequired()], default="-1")
    permission = RadioField(u'权限', choices=[(permission, permission) for permission in User.PermissionList],
                            default=User.Permission.COLLEGE)

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.department.choices = [("-1", u"--- 请选择 ---")] + [(department, department) for department in DepartmentList]

    def validate_department(form, field):
        if field.data == "-1":
            raise ValidationError(u'请下拉选择一个选项')

    def validate_password(form, field):
        u = User.get_by_username(form.username.data)
        if not u.verify_password(field.data):
            raise ValidationError(u'原密码输入错误')


class TeacherForm(Form):
    name = StringField(u'教师姓名', validators=[MyDataRequired()])
    department = SelectField(u'学院', validators=[MyDataRequired()],
                             choices=[(department, department) for department in DepartmentList])


class ContestSeriesForm(Form):
    name = StringField(u'竞赛系列名', validators=[MyDataRequired()])
    budget_text = TextAreaField(u'系列介绍', validators=[MyDataRequired()])

class ContestLevelForm(Form):
    name = StringField(u'竞赛等级名',validators=[MyDataRequired()])
    budget_text = TextAreaField(u'等级介绍', validators=[MyDataRequired()])

class AwardsLevelForm(Form):
    name = StringField(u'奖项等级名',validators=[MyDataRequired()])
    budget_text = TextAreaField(u'等级介绍', validators=[MyDataRequired()])

class ContestResultForm(Form):
    name = StringField(u'竞赛档次名',validators=[MyDataRequired()])
    budget_text = TextAreaField(u'档次介绍', validators=[MyDataRequired()])

class DateRangeField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return self.data[0] + ' - ' + self.data[1]
        else:
            return ''

    def process_formdata(self, value_list):
        if value_list:
            self.data = [d.strip() for d in value_list[0].split('-')]
        else:
            self.data = []

class AwardsDateFiled(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return self.data
        else:
            return ''

    def process_formdata(self, value_list):
        if value_list:
            self.data = value_list
        else:
            self.data = []

class ContestForm(Form):
    name_cn = StringField(u'竞赛中文名', validators=[MyDataRequired()])
    name_en = StringField(u'竞赛英文名', validators=[Optional()])
    #level = SelectField(u'竞赛等级', validators=[MyDataRequired()],
     #                  choices=[(v, v) for v in Contest.ContestLevel],
      #                 default=Contest.ContestLevel[0])
    level_id = SelectField(u'竞赛等级', coerce=int,validators=[Optional()],default=-1)
    type = SelectField(u'竞赛类型', validators=[MyDataRequired()], default="-1")
    #type = StringField(u'竞赛类型', validators=[MyDataRequired()])
    department = SelectField(u'所属部门', validators=[MyDataRequired()], default="-1")

    site = StringField(u'竞赛官网网址', validators=[Optional()])
    organizer = StringField(u'主办方', validators=[MyDataRequired()])
    co_organizer = StringField(u'承办方', validators=[Optional()])
    #year = SelectField(u'年份', coerce=int, default=date.today().year)
    date_range = DateRangeField(u'起止日期', validators=[MyDataRequired()],
                                default=[date.today().strftime('%Y/%m/%d'),
                                         date.today().strftime('%Y/%m/%d')])

    place = StringField(u' ', validators=[Optional()])
    series_id = SelectField(u'所属竞赛系列', coerce=int, validators=[Optional()], default=-1)

    budget = FloatField(u'总费用', validators=[MyDataRequired()])
    budget_text = TextAreaField(u'预算方案', validators=[MyDataRequired()])
    student_num = IntegerField(u'预计参赛人数', validators=[MyDataRequired()])
    teacher_num = IntegerField(u'指导教师人数', validators=[MyDataRequired()])
    # subject = StringField(u'面向专业', validators=[MyDataRequired()])

    def __init__(self, *args, **kwargs):
        super(ContestForm, self).__init__(*args, **kwargs)
        #cur_year = date.today().year
        # self.year.choices = [(year, year) for year in range(cur_year - 1, cur_year + 2)]
        series_list = ContestSeries.get_all()
        level_list = ContestLevel.get_all()
        self.series_id.choices = [(-1, u'--- 请选择 --- ')] + [(series.id, series.name) for series in series_list]
        self.type.choices = [("-1", u"--- 请选择 ---")] + [(t, t) for t in Contest.ContestType]
        self.level_id.choices = [("-1", u"--- 请选择 ---")] + [(level.id, level.name) for level in level_list]
        self.department.choices = [("-1", u"--- 请选择 ---")] + [(department, department) for department in DepartmentList]

    def validate_type(form, field):
        if field.data == "-1":
            raise ValidationError(u'请下拉选择一个选项')

    def validate_department(form, field):
        if field.data == "-1":
            raise ValidationError(u'请下拉选择一个选项')



class TagListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return u', '.join(self.data)
        else:
            return u''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = filter(lambda x: x != '', [x.strip() for x in valuelist[0].split(',')])
        else:
            self.data = []


class AwardsForm(Form):
    honor = StringField(u'奖项名称', validators=[MyDataRequired1()])
    level = SelectField(u'获奖等级')
    title = StringField(u'作品名称', validators=[MyDataRequired1()])
    type = RadioField(u'奖励类型', choices=[(v, v) for v in Awards.AwardsType], default=Awards.AwardsType[0])
    teachers = TagListField(u'', validators=[MyDataRequired()])
    students = TagListField(u'',validators=[MyDataRequired()])
    type1 = StringField(u'奖项类型', validators=[Optional()])
    level1 = StringField(u'获奖等级', validators=[Optional()])
    department = SelectField(u'所属部门', validators=[MyDataRequired()], default="-1")
    year = SelectField(u'获奖年份')
    data = AwardsDateFiled(u'获奖时间',validators=[MyDataRequired()],
                                default=date.today().strftime('%Y/%m/%d')
                                         )
    def __init__(self, *args, **kwargs):
        super(AwardsForm, self).__init__(*args, **kwargs)
        cur_year = date.today().year
        # self.year.choices = [(year, year) for year in range(cur_year - 1, cur_year + 2)]
        self.level.choices = [(v, v) for v in Awards.LevelList()]
        self.year.choices = [(str(y),str(y)) for y in range(cur_year - 4 ,cur_year + 1)]
        self.department.choices = [("-1", u"--- 请选择 ---")] + [(department, department) for department in DepartmentList]

    def get_teacher_list(self):
        # import re
        # items = re.split(ur'[\、\,\，\s\;\；]+', self.teachers.data)
        # teachers = []
        # for item in items:
        #     has_t = Teacher.get_by_name(item)
        #     if has_t is not None:
        #         teachers.append(has_t)
        # return teachers
        teachers = []
        # n = 0
        # print 1112222222222
        # h = Teacher.get_all()
        # for a in h:
        #     print h[n].name
        #     n = n + 1
        for item in self.teachers.data:
            if item == '':
                continue
            has_t = Teacher.get_by_name(item)
            if has_t is not None:
                teachers.append(has_t)
        return teachers

    def get_student_list(self):
        students = []
        for item in self.students.data:
            if item == '':
                continue
            has_t = Student.get_by_stu_no(item)
            if has_t is not None:
                students.append(has_t)
        return students

    def validate_students(form, field):
        if field.data == []:
            raise ValidationError(u'获奖学生不能为空')


class StudentForm(Form):
    stu_no = StringField(u'学号', validators=[MyDataRequired()])
    name = StringField(u'姓名', validators=[MyDataRequired()])
    department = SelectField(u'学院', validators=[MyDataRequired()],
                             choices=[(department, department) for department in DepartmentList])
    major = StringField(u'专业')
    grade = SelectField(u'年级')

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        cur_year = date.today().year
        self.grade.choices = [(str(y), str(y)) for y in range(cur_year, cur_year - 10, -1)]

