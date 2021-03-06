import traceback
from flask import current_app
from flask_restful import reqparse, Resource
from ..models.netflix import Episodes, Shows, EpisodeComments
from flask_restful_swagger import swagger
from flask_restful import fields, inputs
from ..utils.netflix_api import NetflixClient
from datetime import datetime

@swagger.model
class GenericResponse:
    resource_fields = {
        "status": fields.String,
        "message": fields.String,
    }
    required = ['status', 'message']

@swagger.model
class NestedShowObj:
    resource_fields = {
        "id": fields.Integer,
        "title": fields.String,
        "year": fields.String,
        "released": fields.DateTime,
        "plot": fields.String,
        "imdb_rating": fields.Float,
        "seasons": fields.Integer,
        "language": fields.String,
        "updated_on": fields.DateTime,
    }

@swagger.model
@swagger.nested(data=NestedShowObj.__name__)
class ShowDataResponse:
    resource_fields = {
        "status": fields.String,
        "data": fields.List(fields.Nested(NestedShowObj.resource_fields)),
    }
    required = ['status', 'data']

class NestedEpisodeObj:
    resource_fields = {
        "id": fields.Integer,
        "show_id": fields.String,
        "year": fields.String,
        "season": fields.Integer,
        "episode": fields.Integer,
        "title": fields.String,
        "released": fields.DateTime,
        "plot": fields.String,
        "imdb_rating": fields.Float,
        "language": fields.String,
    }
@swagger.model
@swagger.nested(data=NestedEpisodeObj.__name__)
class EpisodeDataResponse:
    resource_fields = {
        "status": fields.String,
        "data": fields.List(fields.Nested(NestedEpisodeObj.resource_fields)),
    }
    required = ['status', 'data']


class ShowsResource(Resource):
    @swagger.operation(
        responseClass=ShowDataResponse.__name__,
        responseMessages=[
            {"code": 200, "message": "Successful Request"},
            {"code": 400, "message": "Invalid Request"},
            {"code": 500, "message": "Unexpected error"},
        ]
    )
    def get(self):
        """ Gets List of Shows """
        try:
            shows = Shows.query.all()
            filtered_shows = [{
                'id': show.id,
                'title': show.title,
                'year': show.year,
                'released': str(show.released),
                'plot': show.plot,
                'imdb_rating': show.imdb_rating,
                'seasons': show.seasons,
                'language': show.language,
                'updated_on': str(show.updated_on)
            } for show in shows]

            return {'status': 'ok',
                    'data': filtered_shows}, 200
        except Exception as ex:
            return {'status': 'error',
                    'message': 'Unexpected Error in ShowsResource get',
                    'error': str(ex)}, 500


    @swagger.model
    class AddShowRequest:
        resource_fields = {
            "show_title": fields.String,
        }
        required = ['show_title']
    @swagger.operation(
        responseClass=GenericResponse.__name__,
        parameters=[{
                "dataType": AddShowRequest.__name__,
                "name": "payload", "required": True, "allowMultiple": False, "paramType": "body",
            },],
        responseMessages=[
            {"code": 200, "message": "Successful Request"},
            {"code": 400, "message": "Invalid Request"},
            {"code": 500, "message": "Unexpected error"},
        ]
    )
    def post(self):
        """ Adds show to DB """
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('show_title', required=True, type=str)
            args = parser.parse_args()
        except:
            return {'status': 'error', 'message': 'Invalid Request'}, 400
        try:
            show_title = args.get('show_title')
            client = NetflixClient()
            response = client.get({'t': show_title})

            try:
                show_json = response.json()
            except ValueError:
                return {'status': 'malformed_response',
                        'message': 'Malformed Response from Show Information request'}, 400

            if show_json.get('Error'):
                return {'status': 'error', 'message': 'Title not recognised'}, 400
            show_json = response.json()

            duplicate = Shows.query.filter(Shows.title==show_json.get('Title')).count()
            if duplicate:
                return {'status': 'error', 'message': 'Show Already Added'}, 500
            if show_json.get('Type') != 'series':
                return {'status': 'error', 'message': 'This is not a series'}, 400

            # timestr format = "17 Apr 2011"
            show_release_str =show_json.get('Released')
            show_time_obj = datetime.strptime(show_release_str, '%d %b %Y')

            total_seasons = int(show_json.get('totalSeasons'))

            show = Shows(
                title = show_json.get('Title'),
                year = show_json.get('Year'),
                released = show_time_obj,
                plot = show_json.get('Plot'),
                imdb_rating = show_json.get('imdbRating'),
                seasons = total_seasons,
                language = show_json.get('Language'),
            )

            current_app.db.session.add(show)
            current_app.db.session.commit()

            return {'status': 'ok', 'message': f'Show {show.title} added to db'}, 200

        except Exception as ex:
            return {'status': 'error',
                    'message': 'Unexpected Error in ShowsResource post',
                    'error': str(ex)}, 500

class DeleteShowsResource(Resource):
    @swagger.operation(
        responseClass=GenericResponse.__name__,
        responseMessages=[
            {"code": 200, "message": "Successful Request"},
            {"code": 500, "message": "Unexpected error"},
        ]
    )
    def delete(self, show_id):
        try:
            show = Shows.query.get(show_id)
            if not show:
                return {'status': 'error', 'message': 'Invalid Show ID'}, 500
            show_title = show.title
            Shows.query.filter(Shows.id == show_id).delete()
            current_app.db.session.commit()
            return {'status': 'ok', 'message': f'Show {show_title} deleted from db'}, 200
        except Exception as ex:
            return {'status': 'error',
                    'message': 'Unexpected Error in DeleteShowsResource delete',
                    'error': str(ex)}, 500


class EpisodesResource(Resource):
    @swagger.operation(
        responseClass=GenericResponse.__name__,
        responseMessages=[
            {"code": 200, "message": "Successful Request"},
            {"code": 400, "message": "Invalid Request"},
            {"code": 500, "message": "Unexpected error"},
        ]
    )
    def post(self, show_id):
        """ adds all episodes for a show - CAN TAKE A WHILE """
        try:
            client = NetflixClient()
            show = Shows.query.get(show_id)
            if not show:
                return {'status': 'error', 'message': 'Invalid Show ID'}, 400

            duplicate = Episodes.query.filter(Episodes.show_id==show_id).count()
            if duplicate:
                return {'status': 'error', 'message': 'Episodes Already Added'}, 400

            total_seasons = show.seasons
            for season in range(1, total_seasons + 1):
                response = client.get({'t': show.title, 'Season': season})  # , 'Episode': 1
                try:
                    season_json = response.json()
                except ValueError:
                    return {'status': 'malformed_response',
                            'message': 'Malformed Response from Season Information request'}, 400

                if season_json.get('Error'):
                    return {'status': 'error', 'message': f'Season {season} not recognised'}, 500

                episodes = [int(episode_data.get('Episode')) for episode_data in season_json.get('Episodes')]
                for episode in episodes:
                    # return [show.title, season, episode]
                    response = client.get({'t': show.title, 'Season': season, 'Episode': episode})
                    try:
                        episode_json = response.json()
                    except ValueError:
                        return {'status': 'malformed_response',
                                'message': 'Malformed Response from Episode Information request'}, 400

                    episode_release_str = episode_json.get('Released')
                    episode_time_obj = datetime.strptime(episode_release_str, '%d %b %Y')

                    ep = Episodes(
                        show_id=show_id,
                        year=episode_json.get('Year'),
                        season=season,
                        episode=episode,
                        title=episode_json.get('Title'),
                        released=episode_time_obj,
                        plot=episode_json.get('Plot'),
                        imdb_rating=episode_json.get('imdbRating'),
                        language=episode_json.get('Language'),
                    )
                    current_app.db.session.add(ep)

            current_app.db.session.commit()
            return {'status': 'ok',
                    'message': f'{Episodes.query.filter(Episodes.show_id==show_id).count()} Episodes Added'}, 400
        except Exception as ex:
            return {'status': 'error',
                    'message': 'Unexpected Error in EpisodesResource post',
                    'error': str(ex)}, 500

class GetEpisodesResource(Resource):
    @swagger.operation(
        responseClass=EpisodeDataResponse.__name__,
        responseMessages=[
            {"code": 200, "message": "Successful Request"},
            {"code": 400, "message": "Invalid Request"},
            {"code": 500, "message": "Unexpected error"},
        ]
    )
    def get(self, show_id, season, minimum_imdb_rating):
        """ Gets list of episodes using season and min IMDB rating (send 0 to not filter) """
        try:
            show = Shows.query.get(show_id)
            if not show:
                return {'status': 'error', 'message': 'Invalid Show ID'}, 400

            episodes = show.episodes

            if int(season):
                episodes = [ep for ep in episodes if ep.season == int(season)]

            if float(minimum_imdb_rating):
                episodes = [ep for ep in episodes if ep.imdb_rating >= float(minimum_imdb_rating)]

            filtered_episodes = [
                {
                'id': ep.id,
                'show_id': ep.show_id,
                'year': ep.year,
                'season': ep.season,
                'episode': ep.episode,
                'title': ep.title,
                'released': str(ep.released),
                'plot': ep.plot,
                'imdb_rating': ep.imdb_rating,
                'language': ep.language,
                } for ep in episodes]
            return {'status': 'ok', 'data': filtered_episodes}, 200

        except Exception as ex:
            return {'status': 'error',
                    'message': 'Unexpected Error in GetEpisodesResource get',
                    'error': str(ex)}, 500

class GetEpisodeByIdResource(Resource):
    @swagger.operation(
        responseClass=EpisodeDataResponse.__name__,
        responseMessages=[
            {"code": 200, "message": "Successful Request"},
            {"code": 400, "message": "Invalid Request"},
            {"code": 500, "message": "Unexpected error"},
        ]
    )
    def get(self, show_id, episode_id):
        """ Gets list of episodes using season and min IMDB rating (send 0 to not filter) """
        try:
            show = Shows.query.get(show_id)
            if not show:
                return {'status': 'error', 'message': 'Invalid Show ID'}, 400

            episode = Episodes.query.get(episode_id)
            if not show:
                return {'status': 'error', 'message': 'Invalid Episode ID'}, 400

            episode_data = {
                'id': episode.id,
                'show_id': episode.show_id,
                'year': episode.year,
                'season': episode.season,
                'episode': episode.episode,
                'title': episode.title,
                'released': str(episode.released),
                'plot': episode.plot,
                'imdb_rating': episode.imdb_rating,
                'language': episode.language,
                }
            return {'status': 'ok', 'data': episode_data}, 200

        except Exception as ex:
            return {'status': 'error',
                    'message': 'Unexpected Error in GetEpisodeByIdResource get',
                    'error': str(ex)}, 500

@swagger.model
class CommentRequet:
    resource_fields = {
        "comment": fields.String,
    }
    required = ['comment']

class GetEpisodeCommentResource(Resource):
    @swagger.operation(
        responseClass=GenericResponse.__name__,
        responseMessages=[
            {"code": 200, "message": "Successful Request"},
            {"code": 400, "message": "Invalid Request"},
            {"code": 500, "message": "Unexpected error"},
        ]
    )
    def get(self, comment_id):
        """ Gets Comment By ID """
        try:
            comment = EpisodeComments.query.get(comment_id)
            if not comment:
                return {'status': 'error', 'message': 'Invalid Comment ID'}, 400
            comment_data = {
                'comment': comment.comment,
                'created_on': str(comment.created_on),
                'updated_on': str(comment.updated_on),
            }
            return {'status': 'ok', 'data': comment_data}, 200

        except Exception as ex:
            return {'status': 'error',
                    'message': 'Unexpected Error in GetEpisodeCommentResource get',
                    'error': str(ex)}, 500

    @swagger.operation(
        responseClass=GenericResponse.__name__,
        responseMessages=[
            {"code": 200, "message": "Successful Request"},
            {"code": 400, "message": "Invalid Request"},
            {"code": 500, "message": "Unexpected error"},
        ]
    )
    def delete(self, comment_id):
        """ Deleted Comment By ID """
        try:
            comment = EpisodeComments.query.get(comment_id)
            if not comment:
                return {'status': 'error', 'message': 'Invalid Comment ID'}, 400
            EpisodeComments.query.filter(EpisodeComments.id==comment_id).delete()
            current_app.db.session.commit()
            return {'status': 'ok', 'message': 'Comment Deleted'}, 200

        except Exception as ex:
            return {'status': 'error',
                    'message': 'Unexpected Error in GetEpisodeCommentResource get',
                    'error': str(ex)}, 500


class UpdateEpisodeCommentsResource(Resource):
    @swagger.operation(
        responseClass=GenericResponse.__name__,
        responseMessages=[
            {"code": 200, "message": "Successful Request"},
            {"code": 400, "message": "Invalid Request"},
            {"code": 500, "message": "Unexpected error"},
        ]
    )
    def put(self, comment_id, comment_text):
        """ Posts Comment on Episode """
        try:
            comment = EpisodeComments.query.get(comment_id)
            if not comment:
                return {'status': 'error', 'message': 'Invalid Comment ID'}, 400

            comment.comment = comment_text
            comment.updated_on = datetime.now()
            current_app.db.session.commit()

            return {'status': 'ok', 'message': 'Comment Posted'}, 200

        except Exception as ex:
            return {'status': 'error',
                    'message': 'Unexpected Error in UpdateEpisodeCommentsResource put',
                    'error': str(ex)}, 500


class EpisodeCommentsResource(Resource):
    @swagger.operation(
        responseClass=GenericResponse.__name__,
        responseMessages=[
            {"code": 200, "message": "Successful Request"},
            {"code": 400, "message": "Invalid Request"},
            {"code": 500, "message": "Unexpected error"},
        ]
    )
    def get(self, episode_id):
        """ Gets List of Comments on episode """
        try:
            episode = Episodes.query.get(episode_id)
            if not episode:
                return {'status': 'error', 'message': 'Invalid Episode ID'}, 400

            comments = episode.comments
            comment_data = [
                {
                    'id': comment.id,
                    'comment': comment.comment,
                    'created_on': str(comment.created_on),
                    'updated_on': str(comment.updated_on)}
            for comment in comments]

            return {'status': 'ok', 'data': comment_data}, 200

        except Exception as ex:
            return {'status': 'error',
                    'message': 'Unexpected Error in EpisodeCommentsResource get',
                    'error': str(ex)}, 500



    @swagger.operation(
        responseClass=GenericResponse.__name__,
        parameters=[{
            "dataType": CommentRequet.__name__,
            "name": "payload", "required": True, "allowMultiple": False, "paramType": "body",
        }, ],
        responseMessages=[
            {"code": 200, "message": "Successful Request"},
            {"code": 400, "message": "Invalid Request"},
            {"code": 500, "message": "Unexpected error"},
        ]
    )
    def post(self, episode_id):
        """ Posts Comment on Episode """
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('comment', required=True, type=str)
            args = parser.parse_args()
        except:
            return {'status': 'error', 'message': 'Invalid Request'}, 400
        try:
            episode = Episodes.query.get(episode_id)
            if not episode:
                return {'status': 'error', 'message': 'Invalid Episode ID'}, 400

            episode_comment = EpisodeComments(
                comment=args.get('comment'),
                episode_id=episode_id,
            )
            current_app.db.session.add(episode_comment)
            current_app.db.session.commit()

            return {'status': 'ok', 'message': 'Comment Posted'}, 200

        except Exception as ex:
            return {'status': 'error',
                    'message': 'Unexpected Error in EpisodeCommentsResource post',
                    'error': str(ex)}, 500