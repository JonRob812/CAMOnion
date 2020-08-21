
from CAMOnion.database.tables import *
from sqlalchemy.orm import sessionmaker
import os

old_database_file = 'camo.db'


old_connection_url = 'mysql+mysqldb://root:123qwe@localhost:3306/camo'

old_engine = create_engine(old_connection_url)
old_Session = sessionmaker(bind=old_engine)
old_session = old_Session()


connection_url = 'sqlite:///C:\\JonRob\\REPO\\CAMOnion\\' + old_database_file

new_engine = create_engine(connection_url)
Session = sessionmaker(bind=new_engine)
session = Session()

old_meta = MetaData()
old_meta.reflect(bind=old_engine)

tables = {Tool_Type:[],
          Feature_Type:[],
          Tool:[],
          CamoOp:[],
          Feature:[],
          Operation:[],
          Machine:[]}


for table in tables:
    results = old_session.query(table)
    print(table)
    for item in results:
        tables[table].append(item)
        local_obj = session.merge(item)
        session.add(local_obj)



session.commit()




