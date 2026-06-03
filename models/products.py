from sqlalchemy import Column, Integer, String, Numeric, Boolean, CHAR
from sqlalchemy.orm import relationship
from semantido.models.declarative_base import SemanticDeclarativeBase


class ProductCatalog(SemanticDeclarativeBase):
    __tablename__ = "products"
    __table_args__ = {"schema": "data_service"}

    prod_id = Column(Integer, primary_key=True, autoincrement=True)
    prod_cd = Column(String(20), nullable=False, unique=True)
    prod_nm = Column(String(100), nullable=False)
    prod_cat = Column(String(20), nullable=False)  # DEPOSIT, LOAN, CARD
    prod_sub_cat = Column(String(20), nullable=True)
    int_rate_pct = Column(Numeric(7, 4), nullable=True)
    fee_monthly_amt = Column(Numeric(10, 2), nullable=True, server_default="0")
    ccy_cd = Column(CHAR(3), nullable=True, server_default="GBP")
    is_avail_flg = Column(Boolean, nullable=False, server_default="true")

    account_maps = relationship("AccountProductMap", back_populates="product")

    def __repr__(self) -> str:
        return (
            f"<ProdCatalog(prod_id={self.prod_id!r}, "
            f"prod_cd={self.prod_cd!r}, "
            f"prod_nm={self.prod_nm!r}, "
            f"prod_cat={self.prod_cat!r})>"
        )
