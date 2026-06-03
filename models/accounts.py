from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Date,
    DateTime,
    CHAR,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from semantido.models.declarative_base import SemanticDeclarativeBase


class AccountInfo(SemanticDeclarativeBase):
    __tablename__ = "acct_info"
    __table_args__ = {"schema": "data_service"}

    acct_id = Column(Integer, primary_key=True, autoincrement=True)
    acct_no = Column(String(20), nullable=False, unique=True)
    prod_id = Column(
        Integer, ForeignKey("data_service.products.prod_id"), nullable=False
    )
    acct_stat = Column(
        String(10), nullable=False, server_default="ACTIVE"
    )  # ACTIVE, DORMANT, FROZEN, CLOSED
    open_dt = Column(Date, nullable=False)
    curr_bal_amt = Column(Numeric(18, 2), nullable=False, server_default="0")
    avail_bal_amt = Column(Numeric(18, 2), nullable=False, server_default="0")
    od_limit_amt = Column(Numeric(14, 2), nullable=True, server_default="0")
    ccy_cd = Column(CHAR(3), nullable=False, server_default="GBP")
    last_txn_dt = Column(Date, nullable=True)
    created_ts = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    product = relationship("ProductCatalog")
    customer_maps = relationship("CustomerAccountMap", back_populates="account")
    product_maps = relationship("AccountProductMap", back_populates="account")
    transactions = relationship("TransactionLedger", back_populates="account")

    def __repr__(self) -> str:
        return (
            f"<AcctInfo(acct_id={self.acct_id!r}, "
            f"acct_no={self.acct_no!r}, "
            f"acct_stat={self.acct_stat!r}, "
            f"curr_bal_amt={self.curr_bal_amt!r})>"
        )
