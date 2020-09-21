from flask_script import Manager, Command
from flask_migrate import Migrate, MigrateCommand

from app.models import db
from app.app_factory import create_app


# we register 'db' to flask migrate (wrapper for alembic)
# python dbmanager.py db init -> initialise migrations folder
# python dbmanager.py db migrate  -> create migrations from models
# python dbmanager.py db upgrade -> update database to next version
# python dbmanager.py db downgrade -> downgrade db to prev version

def create_db_manager():
    app = create_app()
    migrate = Migrate(app, db)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)
    return manager


if __name__ == '__main__':
    create_db_manager().run()
