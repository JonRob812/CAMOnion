from CAMOnion.database.tables import *
from sqlalchemy.orm import sessionmaker
import os

connection_url = 'sqlite:///C:\\JonRob\\REPO\\CAMOnion\\camo.db'       # sqlite
engine = create_engine(connection_url)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)
