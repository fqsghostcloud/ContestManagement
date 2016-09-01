# coding=utf-8
from flask import Flask
from config import config
from app.models import db
from app.models import User, ContestSeries, Contest, Awards, \
    Student, Teacher, Resource,ContestLevel,AwardsLevel,ContestResult

if __name__ == "__main__":
    app = Flask(__name__)
    app.config.from_object(config['rj'])
    db.init_app(app)
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = User.User(u'admin')
        user.password = 'admin'
        user.department = u'超级用户'
        user.permission = User.Permission.SUPER
        user.save()
