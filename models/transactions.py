from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Numeric,
    Date,
    DateTime,
    CHAR,
    ForeignKey,
    CheckConstraint,
    func,
)
from typing import Optional

from sqlalchemy.orm import relationship
from semantido.models.declarative_base import SemanticDeclarativeBase


class TransactionLedger(SemanticDeclarativeBase):
    __tablename__ = "transactions_ledger"
    __table_args__ = (
        CheckConstraint("amt > 0", name="chk_txn_amt_positive"),
        {"schema": "data_service"},
    )

    txn_id = Column(BigInteger, primary_key=True, autoincrement=True)
    txn_ref = Column(String(30), nullable=False, unique=True)
    acct_id = Column(
        Integer, ForeignKey("data_service.acct_info.acct_id"), nullable=False
    )
    cat_id: Optional[int] = Column(
        Integer, ForeignKey("data_service.txn_cat_ref.cat_id"), nullable=True
    )
    txn_typ = Column(String(10), nullable=False)  # DEBIT, CREDIT, FEE, INTEREST
    txn_dt = Column(Date, nullable=False)
    amt = Column(Numeric(18, 2), nullable=False)
    ccy_cd = Column(CHAR(3), nullable=False, server_default="GBP")
    bal_after_amt = Column(Numeric(18, 2), nullable=True)
    chan_cd = Column(String(10), nullable=True)  # ATM, MOBILE, ONLINE, POS, BACS, CHAPS
    narr_txt = Column(String(255), nullable=True)
    created_ts = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    account = relationship("AccountInfo", back_populates="transactions")
    category = relationship(
        "TransactionCategoryReference", back_populates="transactions"
    )

    def __repr__(self) -> str:
        return (
            f"<TransactionLedger(txn_id={self.txn_id!r}, "
            f"txn_ref={self.txn_ref!r}, "
            f"txn_typ={self.txn_typ!r}, "
            f"amt={self.amt!r})>"
        )
