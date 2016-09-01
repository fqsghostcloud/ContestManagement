# coding=utf-8
import os, traceback
from flask import current_app
from flask.ext.uploads import UploadSet, DEFAULTS, ARCHIVES, UploadNotAllowed
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from . import db


resource_uploader = UploadSet('resource', DEFAULTS + ARCHIVES,
                              default_dest=lambda app: app.instance_root)


class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Unicode(1024), nullable=False)
    upload_time = db.Column(db.DateTime)

    awards_id = db.Column(db.String(128),
                          db.ForeignKey('awards.awards_id', ondelete='CASCADE'),
                          nullable=False)

    awards = db.relationship('Awards',
                             backref=db.backref('resources',
                                                cascade="all, delete-orphan",
                                                passive_deletes=True,
                                                lazy='dynamic'))

    def __repr__(self):
        return '<Resource %s>' % self.filename

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @property
    def url(self):
        return resource_uploader.url(self.filename)

    @property
    def size(self):
        return os.path.getsize(resource_uploader.path(self.filename))


def get_by_id(id):
    return Resource.query.filter(Resource.id == id).first()


def generate_filename(awards):
    last_awards = awards.resources.order_by(Resource.filename.desc()).first()
    if last_awards is None:
        return '0001.'
    else:
        last_awards_dir = last_awards.filename.split('/')
        filename = last_awards_dir[1].split('.')[0]
        new_filename = str(int(filename) + 1).rjust(4, '0') + '.'
        return new_filename


def save_res(storage, awards):
    filename = ''
    try:
        maybe_name = generate_filename(awards)
        filename = resource_uploader.save(storage, folder=awards.awards_id,
                                          name=maybe_name)
        res = Resource()
        res.filename = filename
        res.awards_id = awards.awards_id
        res.upload_time = datetime.now()
        res.save()
        current_app.logger.info(u'创建文件 %s 成功' % filename)
        return 'OK'
    except UploadNotAllowed:
        return u"非法上传"
    except IntegrityError:
        os.remove(resource_uploader.path(filename))
        db.session.rollback()
        return u'文件名已存在'
    except Exception, e:
        current_app.logger.error(u'创建文件失败')
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'


def delete_res(res):
    try:
        file_path = resource_uploader.path(res.filename)
        dir = os.path.split(file_path)[0]
        os.remove(file_path)
        if os.path.isdir(dir) and os.listdir(dir) == []:
            os.rmdir(dir)
        res.delete()
        current_app.logger.error(u'删除文件成功')
        return 'OK'
    except Exception, e:
        current_app.logger.error(u'删除文件失败')
        current_app.logger.error(traceback.format_exc())
        return 'FAIL'
