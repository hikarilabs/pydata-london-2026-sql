from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from semantido.models.declarative_base import SemanticDeclarativeBase


class TransactionCategoryReference(SemanticDeclarativeBase):
    __tablename__ = "txn_cat_ref"
    __table_args__ = {"schema": "data_service"}

    cat_id = Column(Integer, primary_key=True, autoincrement=True)
    cat_cd = Column(String(15), nullable=False, unique=True)
    cat_desc = Column(String(100), nullable=True)
    is_debit_flg = Column(Boolean, nullable=False, server_default="true")

    transactions = relationship("TransactionLedger", back_populates="category")

    def __repr__(self) -> str:
        return (
            f"<TransactionCategoryRef(cat_id={self.cat_id!r}, "
            f"cat_cd={self.cat_cd!r}, "
            f"cat_desc={self.cat_desc!r}, "
            f"is_debit_flg={self.is_debit_flg!r})>"
        )
