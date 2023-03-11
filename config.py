import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    SECRET_KEY = 'this is a secret'


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = \
        'sqlite://'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}