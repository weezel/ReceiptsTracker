from sqlalchemy import Column, Integer as sqlInteger, String as sqlString, Date as sqlDate
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import extern


Base = declarative_base()

# self.session.query(receipt.Receipt).all()

class Receipt(Base):
    __tablename__ = "receipt"
    id = Column(sqlInteger, primary_key=True)
    filename = Column(sqlString, unique=True, nullable=False)
    purchase_date = Column(sqlDate)
    tags = Column(sqlString)
    ocr_text = Column(sqlString)

    def __repr__(self):
        return f"{self.filename}: {purchase_date}, " + \
               f"tags: {self.tags}\nocr: {sel.ocr_text}"

    def as_dict(self):
        return { "filename": self.filename,
                 "purchase_date": self.purchase_date,
                 "tags": self.tags,
                 "ocr_text": self.ocr_text }

engine = create_engine(extern.db_name, echo=False)
Base.metadata.create_all(engine, checkfirst=True)

