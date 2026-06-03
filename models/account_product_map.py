from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Text,
    ForeignKey,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import relationship

from semantido.models.declarative_base import SemanticDeclarativeBase


class AccountProductMap(SemanticDeclarativeBase):
    __tablename__ = "acct_prod_map"
    __table_args__ = (
        UniqueConstraint("acct_id", "prod_id", name="uq_acct_prod"),
        {"schema": "data_service"},
    )

    map_id = Column(Integer, primary_key=True, autoincrement=True)
    acct_id = Column(
        Integer, ForeignKey("data_service.acct_info.acct_id"), nullable=False
    )
    prod_id = Column(
        Integer, ForeignKey("data_service.products.prod_id"), nullable=False
    )
    enrol_dt = Column(Date, nullable=False, server_default=text("CURRENT_DATE"))
    prov_status = Column(
        String(10), nullable=True, server_default="ACTIVE"
    )  # ACTIVE, CANCELLED
    note_txt = Column(Text, nullable=True)

    account = relationship("AccountInfo", back_populates="product_maps")
    product = relationship("ProductCatalog", back_populates="account_maps")

    def __repr__(self) -> str:
        return (
            f"<AccountProductMap(map_id={self.map_id!r}, "
            f"acct_id={self.acct_id!r}, "
            f"prod_id={self.prod_id!r}, "
            f"prov_status={self.prov_status!r})>"
        )
