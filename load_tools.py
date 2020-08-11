import csv
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

with open('tools.csv', newline='') as file:
    reader = csv.DictReader(file)
    for line in reader:
        tool = Tool(qb_id=line['qb id'],
                    diameter=line['Diameter'],
                    tool_number=line['Tool number'],
                    name=line['name'],
                    tool_type_id=line['type id'])
        session.add(tool)
    session.commit()



