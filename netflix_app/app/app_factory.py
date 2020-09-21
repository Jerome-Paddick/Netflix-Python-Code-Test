from flask import Flask
from flask_restful import Api
from .models.core import db
from flask_restful_swagger import swagger
from flask import Flask

def create_app(development=True):
    app = Flask(__name__, instance_relative_config=True)

    if development:
        app.config.from_object('app.config.DevelopmentConfig')
    else:
        app.config.from_object('app.config.TestConfig')
    # app.config.from_pyfile('/usr/src/netflix_app/app/config/netflix.py')

    app.config['SQLALCHEMY_DATABASE_URI'] = \
        "{db_prefix}://{user}:{passwd}@{server}/{db}".format(
        db_prefix=app.config['SQLALCHEMY_DB_PREFIX'],
        user=app.config['POSTGRES_USER'],
        passwd=app.config['POSTGRES_PASSWORD'],
        server=app.config['DB_SERVER'],
        db=app.config['POSTGRES_DB'])
    db.init_app(app)

    # so we can call current_app.db from any resource
    app.db = db

    # api = Api(app)

    # Swagger flask restful API:
    # https://github.com/rantav/flask-restful-swagger
    api = swagger.docs(
        Api(app),
        apiVersion='1.0',
        api_spec_url='/api/api_documentation',
        swaggerVersion='3.0',
        description='Netflix API'
    )

    from .resources.netflix import ShowsResource
    from .resources.netflix import DeleteShowsResource
    api.add_resource(ShowsResource, '/api/shows')
    api.add_resource(DeleteShowsResource, '/api/shows/<show_id>')

    from .resources.netflix import EpisodesResource
    from .resources.netflix import GetEpisodesResource
    from .resources.netflix import GetEpisodeByIdResource
    api.add_resource(EpisodesResource, '/api/episodes/<show_id>')
    api.add_resource(GetEpisodesResource, '/api/episodes/<show_id>/<season>/<minimum_imdb_rating>')
    api.add_resource(GetEpisodeByIdResource, '/api/episodes/<show_id>/<episode_id>')


    return app


