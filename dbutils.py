import sqlalchemy.exc
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

import extern
from models import Base, Receipt


class DBUtils(object):
    def __init__(self):
        self.engine = create_engine(extern.db_name)
        Base.metadata.bind = self.engine
        DBSession = sessionmaker(bind=self.engine)
        self.session = DBSession()
    def close(self):
        try:
            self.session.commit()
        except sqlalchemy.exc.IntegrityError:
            print("Broke integrity, cannot continue")
        self.session.close()

    def add(self, r):
        insert_cmd = Receipt.__table__.insert(
                #prefixes=['OR UPDATE'],
                values=r.as_dict())
        self.session.execute(insert_cmd)
        self.session.commit()

