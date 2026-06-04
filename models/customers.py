from semantido import semantic_table
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from semantido.models.declarative_base import SemanticDeclarativeBase
from semantido.generators.semantic_layer import PrivacyLevel


@semantic_table(
    description="Core customer identity record (CIF). Root entity for all customer-level relationships. Include this table ONLY when the query requires a customer attribute — name, segment, KYC status, or contact details. For account-level or product-level analysis with no customer dimension, join directly from acct_info.",
    synonyms=["customer", "client", "account holder", "CIF"],
    sql_filters=["WHERE", "JOIN", "ORDER BY"],
    application_context="Root entity for all customer data. Join to cust_acct_map only when scoping to a specific customer. For analytical queries that do not reference customer attributes, models should bypass this table and start from acct_info directly.",
)
class Customer(SemanticDeclarativeBase):
    __tablename__ = "customer"
    __table_args__ = {"schema": "data_service"}

    cust_id = Column(Integer, primary_key=True, autoincrement=True)
    cust_id_description = (
        "Primary key — internal customer identifier. Auto-incremented by the database."
    )
    cust_id_privacy_level = PrivacyLevel.PUBLIC

    cust_ref_no = Column(String(20), nullable=False, unique=True)
    cust_ref_no_description = "Business-facing CIF reference number. Use in SELECT output to identify a customer — do not use the surrogate cust_id."
    cust_ref_no_privacy_level = PrivacyLevel.PUBLIC
    cust_ref_no_example = ["CIF-001", "CIF-005"]

    f_name = Column(String(80), nullable=False)
    f_name_description = "Customer first (given) name."
    f_name_privacy_level = PrivacyLevel.CONFIDENTIAL

    l_name = Column(String(80), nullable=False)
    l_name_description = "Customer last (family / surname) name."
    l_name_privacy_level = PrivacyLevel.CONFIDENTIAL

    cust_seg = Column(String(20), nullable=True, default="RETAIL")
    cust_seg_description = "Customer segment classification. RETAIL = personal customers, HNW = High Net Worth, SME = Small & Medium Enterprise, CORP = Corporate. Use in WHERE / GROUP BY for segment-level analysis."
    cust_seg_privacy_level = PrivacyLevel.PUBLIC
    cust_seg_example = ["RETAIL", "HNW", "SME", "CORP"]

    kyc_stat = Column(String(10), nullable=False, default="PENDING")
    kyc_stat_description = "Know Your Customer verification status. PENDING = awaiting documents, VERIFIED = checks passed, FAILED = checks failed or expired. Filter to kyc_stat = 'VERIFIED' for operational queries unless the question specifically asks about unverified customers."
    kyc_stat_privacy_level = PrivacyLevel.PUBLIC
    kyc_stat_example = ["PENDING", "VERIFIED", "FAILED"]

    prim_email = Column(String(150), nullable=True)
    prim_email_description = "Primary email address used for statements, alerts, and marketing communications."
    prim_email_privacy_level = PrivacyLevel.CONFIDENTIAL

    created_ts = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_ts_description = "Timestamp (with timezone) when this customer record was first created. Defaults to NOW()."
    created_ts_privacy_level = PrivacyLevel.PUBLIC

    last_upd_ts = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_upd_ts_description = "Timestamp of the most recent update to this record. Should be maintained by the application layer on every write."
    last_upd_ts_privacy_level = PrivacyLevel.PUBLIC

    account_maps = relationship("CustomerAccountMap", back_populates="customer")

    def __repr__(self) -> str:
        return (
            f"<CustMaster(cust_id={self.cust_id!r}, "
            f"cust_ref_no={self.cust_ref_no!r}, "
            f"f_name={self.f_name!r}, "
            f"l_name={self.l_name!r})>"
        )
