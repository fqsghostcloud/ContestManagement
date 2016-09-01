from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def load_department_config(destination):
    from codecs import open as codecs_open
    cfg = codecs_open(destination, 'r', 'utf-8')
    department_list = [line.strip() for line in cfg]
    cfg.close()
    return department_list
