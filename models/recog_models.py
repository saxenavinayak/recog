from sqlalchemy import Column, Integer, String
from pgvector.sqlalchemy import Vector
from helpers.db_connector import Base, engine


class PhotoResource(Base):
    __tablename__ = 'image_analysis'

    id = Column(Integer, primary_key=True, index=True)

    image_name = Column(String, nullable=False)
    norm_embedded_tensor = Column(Vector(512), nullable=False)
    bounding_box = Column(Vector(4), nullable=False)

    label = Column(Integer, nullable=True)


class PersonCandidate(Base):
    __tablename__ = 'entity_embeddings'

    id = Column(Integer, primary_key=True, index=True)
    image_name = Column(String, nullable=False)
    person_name = Column(String, nullable=True) # This would be user defined
    embedding = Column(Vector(512), nullable=False)






Base.metadata.create_all(bind=engine)
