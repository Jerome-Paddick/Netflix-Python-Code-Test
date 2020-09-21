class Config(object):
    DEBUG = False
    TESTING = False

    API_PROTOCOL='http'
    API_ADDRESS='www.omdbapi.com'
    API_KEY="e880cf92"
    API_PORT="80"
    API_URL="http://www.omdbapi.com/?t="
    API_VERIFY_SSL_CERT=True
    SQLALCHEMY_TRACK_MODIFICATIONS=False

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    # DEBUG=True

    SERVER_NAME = 'localhost:5000'
    POSTGRES_USER = 'admin'
    POSTGRES_PASSWORD = 'S8bamnevYx8JaxQgeDSekEtETtkRGSJ4cBs3'
    POSTGRES_DB = 'netflix_db'
    DB_SERVER = 'postgres:5432'
    SQLALCHEMY_DB_PREFIX = "postgresql+psycopg2"

    SECRET_KEY = ""
    SECURITY_PASSWORD_SALT = ""

    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_CHANGEABLE = True

class TestConfig(Config):
    TESTING = True

    SERVER_NAME = 'localhost:5000'
    POSTGRES_USER = 'admin'
    POSTGRES_PASSWORD = 'S8bamnevYx8JaxQgeDSekEtETtkRGSJ4cBs3'
    POSTGRES_DB = 'test_db'
    DB_SERVER = 'postgres:5432'
    SQLALCHEMY_DB_PREFIX = "postgresql+psycopg2"

    SECRET_KEY = ""
    SECURITY_PASSWORD_SALT = ""

    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_CHANGEABLE = True

