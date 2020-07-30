from CAMOnion.database.tables import *
from sqlalchemy.orm import sessionmaker
import os

database_file = 'camo.db'
#
# if database_file in os.listdir('.'):
#     os.remove(database_file)

connection_url = 'sqlite:///C:\\JonRob\\REPO\\CAMOnion\\' + database_file

engine = create_engine(connection_url)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

