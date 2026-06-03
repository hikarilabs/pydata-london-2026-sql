from sqlalchemy import Column, Integer, String, DateTime, func
from models import Base


class Customers(Base):
    __tablename__ = "customer"
    __table_args__ = {"schema": "data_service"}

    cust_id = Column(Integer, primary_key=True, autoincrement=True)
    cust_ref_no = Column(String(20), nullable=False, unique=True)
    f_name = Column(String(80), nullable=False)
    l_name = Column(String(80), nullable=False)
    cust_seg = Column(String(20), nullable=True, default="RETAIL")  # RETAIL, HNW, SME
    kyc_stat = Column(
        String(10), nullable=True, default="PENDING"
    )  # PENDING, VERIFIED, FAILED
    prim_email = Column(String(150), nullable=True)
    created_ts = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_ts = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:
        return (
            f"<CustMaster(cust_id={self.cust_id!r}, "
            f"cust_ref_no={self.cust_ref_no!r}, "
            f"f_name={self.f_name!r}, "
            f"l_name={self.l_name!r})>"
        )
