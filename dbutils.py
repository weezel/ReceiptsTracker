import sqlalchemy.exc
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

import extern
from models import Base, Tag, Receipt


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

    def add(self, receipt, tags):
        #receipt_insert_cmd = Receipt.__table__.insert(
                #prefixes=['OR UPDATE'],
                #values=receipt.as_dict())
        #res = self.session.execute(receipt_insert_cmd)
        for tag in tags:
            receipt.tag.append(tag)
        self.session.add(receipt)

        self.session.commit()

