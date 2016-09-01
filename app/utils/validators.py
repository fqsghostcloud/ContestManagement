# coding=utf-8
from wtforms.validators import DataRequired

class MyDataRequired(DataRequired):

    def __init__(self):
        super(MyDataRequired, self).__init__(u'')

class MyDataRequired1(DataRequired):

    def __init__(self):
        super(MyDataRequired1, self).__init__(u'必填项！')