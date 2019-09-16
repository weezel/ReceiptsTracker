from sqlalchemy import Column, Integer, String
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import extern


Base = declarative_base()

# self.session.query(receipt.Receipt).all()

class Receipt(Base):
    __tablename__ = "receipt"
    id = Column(Integer, primary_key=True)
    filename = Column(String, unique=True)
    tags = Column(String)
    ocr_text = Column(String)

    def __repr__(self):
        return "{}: {}\n{}" \
                .format(self.filename, \
                self.tags, \
                self.ocr_text)

    def as_dict(self):
        return { "filename" : self.filename,
                 "tags" : self.tags,
                 "ocr_text" : self.ocr_text }


engine = create_engine(extern.db_name, echo=False)
Base.metadata.create_all(engine, checkfirst=True)

