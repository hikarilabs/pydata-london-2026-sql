from semantido import semantic_table
from semantido.generators.semantic_layer import PrivacyLevel
from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import relationship
from semantido.models.declarative_base import SemanticDeclarativeBase

@semantic_table(
    description="Resolves the many-to-many relationship between customers and accounts. Supports joint accounts, power-of-attorney mandates, and corporate account signatories. A single account can have multiple customer relationships; a customer can hold multiple accounts.",
    synonyms=["customer account link", "account holder", "joint account", "mandate", "signatory", "power of attorney"],
    sql_filters=["WHERE", "JOIN", "ORDER BY"],
    application_context=(
        "The primary join path from customer to account. Always filter by cust_id to scope to the authenticated customer. "
        "Use eff_to_dt IS NULL to return only currently active relationships. "
        "rel_typ indicates the nature of the relationship — use to distinguish owners (PRIMARY, JOINT) from authorised parties (MANDATE, SIGNATORY)."
    ),
)
class CustomerAccountMap(SemanticDeclarativeBase):
    __tablename__ = "cust_acct_map"
    __table_args__ = (
        UniqueConstraint("cust_id", "acct_id", "rel_typ", name="uq_cust_acct_rel"),
        {"schema": "data_service"},
    )

    map_id = Column(Integer, primary_key=True, autoincrement=True)
    map_id_description = "Surrogate primary key for this mapping row."
    map_id_privacy_level = PrivacyLevel.PUBLIC

    cust_id = Column(
        Integer, ForeignKey("data_service.customer.cust_id"), nullable=False
    )
    cust_id_description = "Foreign key to data_service.customer.cust_id."
    cust_id_privacy_level = PrivacyLevel.PUBLIC

    acct_id = Column(
        Integer, ForeignKey("data_service.acct_info.acct_id"), nullable=False
    )
    acct_id_description = "Foreign key to data_service.acct_info.acct_id."
    acct_id_privacy_level = PrivacyLevel.PUBLIC

    rel_typ = Column(
        String(20), nullable=False, server_default="PRIMARY"
    )  # PRIMARY, JOINT, MANDATE
    rel_typ_description = "Nature of the customer's relationship to the account. PRIMARY = sole or lead account holder, JOINT = co-owner with equal rights, MANDATE = third party with operating authority (e.g. power of attorney), SIGNATORY = corporate account signatory."
    rel_typ_privacy_level = PrivacyLevel.PUBLIC
    rel_typ_example = ["PRIMARY", "JOINT", "MANDATE", "SIGNATORY"]

    eff_from_dt = Column(Date, nullable=False, server_default=text("CURRENT_DATE"))
    eff_from_dt_description = "Date from which this customer-account relationship is effective."
    eff_from_dt_privacy_level = PrivacyLevel.PUBLIC
    eff_from_dt_example = ["2020-01-01", "2023-06-15"]

    eff_to_dt = Column(Date, nullable=True)
    eff_to_dt_description = "Date on which the relationship ended (e.g. mandate revoked, joint holder removed). NULL = still active."
    eff_to_dt_privacy_level = PrivacyLevel.PUBLIC
    eff_to_dt_example = ["2024-12-31", None]

    customer = relationship("Customer", back_populates="account_maps")
    account = relationship("AccountInfo", back_populates="customer_maps")

    def __repr__(self) -> str:
        return (
            f"<CustomerAccountMap(map_id={self.map_id!r}, "
            f"cust_id={self.cust_id!r}, "
            f"acct_id={self.acct_id!r}, "
            f"rel_typ={self.rel_typ!r})>"
        )
