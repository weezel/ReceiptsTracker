from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy import Integer as sqlInteger, String as sqlString, Date as sqlDate
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

import extern


Base = declarative_base()

receipt_to_tag_association = Table("receipt_to_tag_association",
        Base.metadata,
        Column("receipt_id", sqlInteger, ForeignKey("receipt.id")),
        Column("tag_id", sqlInteger, ForeignKey("tag.id")))

class Receipt(Base):
    __tablename__ = "receipt"
    id = Column(sqlInteger, primary_key=True)
    filename = Column(sqlString, unique=True, nullable=False)
    purchase_date = Column(sqlDate)
    ocr_text = Column(sqlString)
    tag = relationship("Tag", secondary=receipt_to_tag_association)

    def __repr__(self):
        return f"{self.filename}: {purchase_date},\n" + \
               f"OCR: {sel.ocr_text}"

    def as_dict(self):
        return { "filename": self.filename,
                 "purchase_date": self.purchase_date,
                 "ocr_text": self.ocr_text }

class Tag(Base):
    __tablename__ = "tag"
    id = Column(sqlInteger, primary_key=True)
    tag = Column(sqlString)

    def as_dict(self):
        return { "tag": self.tag }


engine = create_engine(extern.db_name, echo=False)
Base.metadata.create_all(engine, checkfirst=True)

