import os
from datetime import timedelta

basedir = os.path.split(os.path.realpath(__file__))[0]


class Constant:
    DEPARTMENT_CONFIG_DEST = basedir + '/department.ini'
    LOG_DIR = basedir + '/log/awards.log'


class Config:
    SSL_DISABLE = True
    CSRF_ENABLED = True
    SECRET_KEY = 'a hard guess string'
    ''' sql '''
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    ''' session, cookie '''
    PERMANENT_SESSION_LIFETIME = timedelta(days=3)
    REMEMBER_COOKIE_DURATION = timedelta(days=3)
    ''' file '''
    UPLOADED_RESOURCE_DEST = basedir + '/uploads/'
    ''' admin '''
    ADMIN_USER_PER_PAGE = 10
    ADMIN_TEACHER_PER_PAGE = 10
    ADMIN_STUDENT_PER_PAGE = 10
    ADMIN_SERIES_PER_PAGE = 10
    ADMIN_CONTEST_PER_PAGE = 10
    ADMIN_AWARDS_PER_PAGE = 10
    ADMIN_APPLY_PER_PAGE = 4
    ADMIN_STATISTICS_PER_PAGE = 4
    ADMIN_CONTESTLEVEL_PER_PAGE = 10
    ADMIN_AWARDSLEVEL_PER_PAGE = 10
    ADMIN_RESULT_PER_PAGE = 10

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mssql+pymssql://sa:rayn2015@localhost:1433/demo?charset=utf8'


class DeployConfig(Config):
    SECRET_KEY = 'gefdger3fs'
    SQLALCHEMY_DATABASE_URI = 'mssql+pymssql://dxy:Dxyrjgcxy2015@210.41.228.124:1433/ACMS?charset=utf8'

class DouConfig(Config):
    SECRET_KEY = '201509'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:201509@121.42.31.81/test?charset=utf8'

class HrConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mssql+pymssql://sa:sq5292016@114.215.119.20/Project?charset=utf8'

class SaConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mssql+pymssql://sa:SQL201509@localhost:1433/Project?charset=utf8'

class RjConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mssql+pymssql://jstd:rjgcxy2016@210.41.225.108:1433/EAS?charset=utf8'

config = {
    'dev': DevConfig,
    'deploy': DeployConfig,
    'dou':DouConfig,
    'hr':HrConfig,
    'sa': SaConfig,
    'default': DevConfig,
    'rj':RjConfig
}
