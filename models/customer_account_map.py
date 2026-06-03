from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import relationship
from semantido.models.declarative_base import SemanticDeclarativeBase


class CustomerAccountMap(SemanticDeclarativeBase):
    __tablename__ = "cust_acct_map"
    __table_args__ = (
        UniqueConstraint("cust_id", "acct_id", "rel_typ", name="uq_cust_acct_rel"),
        {"schema": "data_service"},
    )

    map_id = Column(Integer, primary_key=True, autoincrement=True)
    cust_id = Column(
        Integer, ForeignKey("data_service.customer.cust_id"), nullable=False
    )
    acct_id = Column(
        Integer, ForeignKey("data_service.acct_info.acct_id"), nullable=False
    )
    rel_typ = Column(
        String(20), nullable=False, server_default="PRIMARY"
    )  # PRIMARY, JOINT, MANDATE
    eff_from_dt = Column(Date, nullable=False, server_default=text("CURRENT_DATE"))
    eff_to_dt = Column(Date, nullable=True)

    customer = relationship("Customer", back_populates="account_maps")
    account = relationship("AccountInfo", back_populates="customer_maps")

    def __repr__(self) -> str:
        return (
            f"<CustomerAccountMap(map_id={self.map_id!r}, "
            f"cust_id={self.cust_id!r}, "
            f"acct_id={self.acct_id!r}, "
            f"rel_typ={self.rel_typ!r})>"
        )
