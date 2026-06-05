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
    description=(
        "Bridge table tracking add-on product enrolments on accounts. "
        "One account can have multiple active add-on rows (e.g. a debit card "
        "AND a business overdraft enrolled on the same account). "
        "FILTER-ONLY TABLE: never use as a JOIN path for balance aggregation — "
        "it will emit multiple curr_bal_amt rows per account, inflating every "
        "SUM and AVG. Always use an EXISTS subquery to filter qualifying accounts, "
        "keeping the balance aggregation on acct_info directly:\n"
        "  WHERE EXISTS (\n"
        "    SELECT 1 FROM acct_prod_map m\n"
        "    JOIN prod_catalog p ON p.prod_id = m.prod_id\n"
        "    WHERE m.acct_id = a.acct_id\n"
        "      AND m.prov_status = 'ACTIVE'\n"
        "      AND <condition>\n"
        "  )"
    ),
    synonyms=[
        "add-on",
        "supplementary product",
        "overdraft facility",
        "packaged product",
        "product enrolment",
    ],
    sql_filters=["WHERE", "JOIN", "ORDER BY"],
    application_context=(
        "Use EXISTS subqueries only — never join this table for balance aggregation. It has multiple rows per account and will inflate SUM/AVG. Filter usage: WHERE EXISTS (SELECT 1 FROM acct_prod_map m WHERE m.acct_id = a.acct_id AND m.prov_status = 'ACTIVE' AND ...)."
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

    prov_status = Column(String(10), nullable=True, server_default="ACTIVE")
    prov_status_description = (
        "Enrolment status. Values: ACTIVE, CANCELLED. "
        "Always filter to prov_status = 'ACTIVE' in EXISTS subqueries."
    )
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
