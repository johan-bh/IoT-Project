import os

class Config:
    """Set Flask config variables."""
    SECRET_KEY = '***********'
    # MAX_CONTENT_LENGTH = 2024 * 2024
    UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif', "PNG", "JPG", "JPEG", "BMP"]
    UPLOAD_PATH = 'static/images'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///images.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    S3_BUCKET = os.environ.get('BUCKETEER_BUCKET_NAME')
    S3_KEY = os.environ.get('BUCKETEER_AWS_ACCESS_KEY_ID')
    S3_SECRET = os.environ.get('BUCKETEER_AWS_SECRET_ACCESS_KEY')
