# models.py
from sqlalchemy import Column, Integer, String, JSON
from database import Base

class Rule(Base):
    __tablename__ = 'rule'

    id = Column(Integer, primary_key=True, index=True)
    rule_string = Column(String, nullable=False)
    ast_json = Column(JSON, nullable=False)  # Store the AST in JSON format
