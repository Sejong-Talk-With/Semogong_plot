import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import boto3

from make_plot import query_table, make_plot

AWS_KEY_ID = os.environ.get("S3_ID")
AWS_SECRET_KEY = os.environ.get("S3_PASSWORD")

name = os.environ.get("DB_NAME")
password = os.environ.get("DB_PASSWORD")
end_point = os.environ.get("DB_URL")
database_name = os.environ.get("DB_NAME_S")

engine = create_engine(f'mysql+pymysql://{name}:{password}@{end_point}/{database_name}')

Session = sessionmaker()
Session.configure(bind=engine)
Base = declarative_base()

db = Session()

result, member_name = query_table(db)
make_plot(result, member_name)

db.close()


s3 = boto3.client('s3', region_name='ap-northeast-2',
                        aws_access_key_id=AWS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_KEY)

s3.upload_file(Bucket='semogong-bucket',
              Filename='my_plot.png',
              Key='my_plot.png',
              ExtraArgs={'ACL':'public-read'})