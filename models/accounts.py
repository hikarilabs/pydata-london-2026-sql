from semantido import semantic_table
from semantido.generators.semantic_layer import PrivacyLevel
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

@semantic_table(
    description="Individual customer account records. Each account is associated with one product and one branch. Balances are stored as point-in-time figures; historical movements are in transactions_ledger.",
    synonyms=["account", "bank account", "current account", "savings account", "loan account", "card account"],
    sql_filters=["WHERE", "JOIN", "ORDER BY"],
    application_context=(
        "Always reach this table via cust_acct_map to scope results to the authenticated customer. "
        "Use curr_bal_amt for ledger balance and avail_bal_amt for drawable funds. "
        "Filter by acct_stat = 'ACTIVE' unless the user explicitly asks about closed or dormant accounts. "
        "Join to products on prod_id for product name, category, and default rate/fee."
    ),
)

class AccountInfo(SemanticDeclarativeBase):
    __tablename__ = "acct_info"
    __table_args__ = {"schema": "data_service"}

    acct_id = Column(Integer, primary_key=True, autoincrement=True)
    acct_id_description = "Primary key for the account."
    acct_id_privacy_level = PrivacyLevel.PUBLIC

    acct_no = Column(String(20), nullable=False, unique=True)
    acct_no_description = "Human-readable account number. Used in statements, payment instructions, and customer communications."
    acct_no_privacy_level = PrivacyLevel.CONFIDENTIAL
    acct_no_example = ["GB00001234567890", "00123456"]

    prod_id = Column(
        Integer, ForeignKey("data_service.products.prod_id"), nullable=False
    )
    prod_id_description = "Foreign key to data_service.products.prod_id. The product this account is opened under. Determines base interest rate, fees, and eligible features."
    prod_id_privacy_level = PrivacyLevel.PUBLIC

    acct_stat = Column(
        String(10), nullable=False, server_default="ACTIVE"
    )  # ACTIVE, DORMANT, FROZEN, CLOSED
    acct_stat_description = "Current account status. ACTIVE = operating normally, DORMANT = no customer-initiated transactions for 12+ months, FROZEN = blocked pending investigation, CLOSED = account closed."
    acct_stat_privacy_level = PrivacyLevel.PUBLIC
    acct_stat_example = ["ACTIVE", "DORMANT", "FROZEN", "CLOSED"]

    open_dt = Column(Date, nullable=False)
    open_dt_description = "Date the account was opened."
    open_dt_privacy_level = PrivacyLevel.PUBLIC
    open_dt_example = ["2018-03-14", "2021-11-01"]

    curr_bal_amt = Column(Numeric(18, 2), nullable=False, server_default="0")
    curr_bal_amt_description = "Current ledger balance — all posted debits and credits included. May differ from avail_bal_amt if pending transactions or holds are applied."
    curr_bal_amt_privacy_level = PrivacyLevel.CONFIDENTIAL
    curr_bal_amt_example = [1250.00, -45.00, 0.00]

    avail_bal_amt = Column(Numeric(18, 2), nullable=False, server_default="0")
    avail_bal_amt_description = "Available balance — the amount the customer can actually draw on. Excludes uncleared credits and any amount under a hold or freeze."
    avail_bal_amt_privacy_level = PrivacyLevel.CONFIDENTIAL
    avail_bal_amt_example = [1200.00, -45.00, 0.00]

    od_limit_amt = Column(Numeric(14, 2), nullable=True, server_default="0")
    od_limit_amt_description = "Arranged overdraft limit in the account currency. Zero if no overdraft facility is attached."
    od_limit_amt_privacy_level = PrivacyLevel.CONFIDENTIAL
    od_limit_amt_example = [500.00, 0.00]

    ccy_cd = Column(CHAR(3), nullable=False, server_default="GBP")
    ccy_cd_description = "ISO 4217 currency the account is denominated in."
    ccy_cd_privacy_level = PrivacyLevel.PUBLIC
    ccy_cd_example = ["GBP", "EUR", "USD"]

    last_txn_dt = Column(Date, nullable=True)
    last_txn_dt_description = "Date of the most recent transaction posted to this account. Used to drive dormancy detection rules."
    last_txn_dt_privacy_level = PrivacyLevel.PUBLIC
    last_txn_dt_example = ["2025-05-30", None]

    created_ts = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_ts_description = "Record creation timestamp."
    created_ts_privacy_level = PrivacyLevel.PUBLIC

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
