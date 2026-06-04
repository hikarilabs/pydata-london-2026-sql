from semantido import semantic_table
from semantido.generators.semantic_layer import PrivacyLevel
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

@semantic_table(
    description="Links accounts to supplementary or add-on products beyond their primary product. Examples include overdraft facilities enrolled on a current account, packaged insurance add-ons, or rewards credit cards linked to a savings account.",
    synonyms=["add-on", "supplementary product", "overdraft facility", "packaged product", "product enrolment"],
    sql_filters=["WHERE", "JOIN", "ORDER BY"],
    application_context=(
        "Join to acct_info on acct_id to get the account, and to products on prod_id to get the add-on product details. "
        "Filter by prov_status = 'ACTIVE' for currently active enrolments. "
        "Use prod_catalog.fee_monthly_amt for the monthly fee applicable to this enrolment."
    ),
)
class AccountProductMap(SemanticDeclarativeBase):
    __tablename__ = "acct_prod_map"
    __table_args__ = (
        UniqueConstraint("acct_id", "prod_id", name="uq_acct_prod"),
        {"schema": "data_service"},
    )

    map_id = Column(Integer, primary_key=True, autoincrement=True)
    map_id_description = "Surrogate primary key."
    map_id_privacy_level = PrivacyLevel.PUBLIC

    acct_id = Column(
        Integer, ForeignKey("data_service.acct_info.acct_id"), nullable=False
    )
    acct_id_description = "Foreign key to data_service.acct_info.acct_id. The account receiving the additional product."
    acct_id_privacy_level = PrivacyLevel.PUBLIC

    prod_id = Column(
        Integer, ForeignKey("data_service.products.prod_id"), nullable=False
    )
    prod_id_description = "Foreign key to data_service.products.prod_id. The add-on product being enrolled."
    prod_id_privacy_level = PrivacyLevel.PUBLIC

    enrol_dt = Column(Date, nullable=False, server_default=text("CURRENT_DATE"))
    enrol_dt_description = "Date the account was enrolled onto this add-on product."
    enrol_dt_privacy_level = PrivacyLevel.PUBLIC
    enrol_dt_example = ["2024-01-15", "2023-09-01"]

    prov_status = Column(
        String(10), nullable=True, server_default="ACTIVE"
    )
    prov_status_description = "Current provisioning status of the add-on."
    prov_status_privacy_level = PrivacyLevel.PUBLIC
    prov_status_example = ["ACTIVE", "SUSPENDED", "CANCELLED"]

    note_txt = Column(Text, nullable=True)
    note_txt_description = "Free-text notes about the enrolment (e.g. reason for fee override, approval reference)."
    note_txt_privacy_level = PrivacyLevel.PUBLIC
    note_txt_example = ["Fee waived — promotional offer ref PRO-2024-001", None]

    account = relationship("AccountInfo", back_populates="product_maps")
    product = relationship("ProductCatalog", back_populates="account_maps")

    def __repr__(self) -> str:
        return (
            f"<AccountProductMap(map_id={self.map_id!r}, "
            f"acct_id={self.acct_id!r}, "
            f"prod_id={self.prod_id!r}, "
            f"prov_status={self.prov_status!r})>"
        )
