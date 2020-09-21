import os
from flask.ext.testing import TestCase

os.environ["DIAG_CONFIG_MODULE"] = "config.test"
from app import app, db


class SQLAlchemyTest(TestCase):

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()