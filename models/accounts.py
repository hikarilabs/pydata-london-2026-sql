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
    description=(
        "Individual account records. Primary entity for account-level analysis. "
        "For product-category breakdowns and balance aggregations with no "
        "customer dimension, join directly to prod_catalog via acct_info.prod_id "
        "— this is a direct 1:1 FK and requires no bridge table. "
        "DEFAULT SCOPE: always apply WHERE acct_stat = 'ACTIVE' for balance "
        "and account-count metrics unless the question explicitly mentions "
        "dormant, closed, or all accounts."
    ),
    synonyms=[
        "account",
        "bank account",
        "current account",
        "savings account",
        "loan account",
        "card account",
    ],
    sql_filters=["WHERE", "JOIN", "ORDER BY"],
    application_context=(
        "Reach via cust_acct_map only when a customer attribute is required (name, segment, KYC). For aggregate balance or product analysis with no customer dimension, join acct_info directly."
        "Use curr_bal_amt for ledger balance and avail_bal_amt for drawable funds. "
        "Filter by acct_stat = 'ACTIVE' unless the user explicitly asks about closed or dormant accounts. "
        "Join to products on prod_id for product name, category, and default rate/fee."
    ),
)
class AccountInfo(SemanticDeclarativeBase):
    __tablename__ = "acct_info"
    __table_args__ = {"schema": "data_service"}

    acct_id = Column(Integer, primary_key=True, autoincrement=True)
    acct_id_description = "Primary key — internal account identifier. Never include in SELECT output. Use only in JOIN and WHERE clauses."
    acct_id_privacy_level = PrivacyLevel.PUBLIC

    acct_no = Column(String(20), nullable=False, unique=True)
    acct_no_description = "Human-readable account number. Use in SELECT output to identify an account — do not expose the primary key acct_id."
    acct_no_privacy_level = PrivacyLevel.CONFIDENTIAL
    acct_no_example = ["GB00001234567890", "00123456"]

    prod_id = Column(
        Integer, ForeignKey("data_service.products.prod_id"), nullable=False
    )
    prod_id_description = (
        "Foreign key to prod_catalog. Direct 1:1 join path for "
        "product-level analysis: JOIN prod_catalog p ON p.prod_id = a.prod_id. "
        "Do not route through cust_acct_map to reach product data."
    )
    prod_id_privacy_level = PrivacyLevel.PUBLIC

    acct_stat = Column(
        String(10), nullable=False, server_default="ACTIVE"
    )  # ACTIVE, DORMANT, FROZEN, CLOSED
    acct_stat_description = (
        "Account lifecycle status. Values: ACTIVE, DORMANT, FROZEN, CLOSED. "
        "DEFAULT FILTER for all balance and count metrics: "
        "WHERE acct_stat = 'ACTIVE'. Always apply unless the question "
        "explicitly asks about dormant, closed, frozen, or all accounts. "
        "Omitting this filter includes zero-balance closed accounts in "
        "averages and inflates portfolio counts."
    )
    acct_stat_privacy_level = PrivacyLevel.PUBLIC
    acct_stat_example = ["ACTIVE", "DORMANT", "FROZEN", "CLOSED"]

    open_dt = Column(Date, nullable=False)
    open_dt_description = "Date the account was opened."
    open_dt_privacy_level = PrivacyLevel.PUBLIC
    open_dt_example = ["2018-03-14", "2021-11-01"]

    curr_bal_amt = Column(Numeric(18, 2), nullable=False, server_default="0")
    curr_bal_amt_description = (
        "Full ledger balance — all posted transactions including "
        "pending holds and uncleared credits. "
        "Use for: regulatory deposit reporting, portfolio totals, "
        "reconciliation against nostro accounts. "
        "Do NOT use for customer-facing balance display or overdraft "
        "risk — use avail_bal_amt for those cases."
    )
    curr_bal_amt_privacy_level = PrivacyLevel.CONFIDENTIAL
    curr_bal_amt_example = [1250.00, -45.00, 0.00]

    avail_bal_amt = Column(Numeric(18, 2), nullable=False, server_default="0")
    avail_bal_amt_description = (
        "Spendable balance — excludes pending direct debit holds and "
        "uncleared inbound transfers. May be lower than curr_bal_amt "
        "when a hold is in place. "
        "Use for: customer-facing balance display, overdraft risk "
        "assessment, payment capacity checks ('can this customer cover "
        "£X?'), card authorisation context. "
        "Do NOT use for regulatory reporting — use curr_bal_amt."
    )
    avail_bal_amt_privacy_level = PrivacyLevel.CONFIDENTIAL
    avail_bal_amt_example = [1200.00, -45.00, 0.00]

    od_limit_amt = Column(Numeric(14, 2), nullable=True, server_default="0")
    od_limit_amt_description = (
        "Arranged overdraft limit in the account currency. "
        "Zero when no overdraft facility is attached to the account. "
        "\n\n"
        "ALWAYS use avail_bal_amt (not curr_bal_amt) alongside this "
        "column — overdraft risk is a function of what the customer "
        "can actually spend, not the ledger balance. "
        "\n\n"
        "Derived metric: "
        "total_headroom = avail_bal_amt + od_limit_amt. "
        "This is the maximum the customer can spend before hitting "
        "an unauthorised overdraft. "
        "\n\n"
        "OVERDRAFT RISK THRESHOLD — two populations, different logic: "
        "\n"
        "Accounts WITH a facility (od_limit_amt > 0): "
        "flag when avail_bal_amt < od_limit_amt * 0.2 "
        "(available balance has fallen below 20 percent of the "
        "arranged limit — less than one fifth of the facility remains). "
        "\n"
        "Accounts WITHOUT a facility (od_limit_amt = 0): "
        "flag when avail_bal_amt < 100 "
        "(below £100 with no safety net — any unexpected debit "
        "creates an unauthorised overdraft immediately). "
        "\n\n"
        "IMPORTANT: a percentage-based threshold collapses to "
        "avail_bal_amt < 0 when od_limit_amt = 0, silently excluding "
        "at-risk no-facility accounts. Always split the WHERE clause "
        "across both populations: "
        "\n"
        "WHERE a.acct_stat = 'ACTIVE' "
        "\n"
        "  AND ( "
        "\n"
        "    (a.od_limit_amt > 0 "
        "AND a.avail_bal_amt < a.od_limit_amt * 0.2) "
        "\n"
        "    OR "
        "\n"
        "    (a.od_limit_amt = 0 "
        "AND a.avail_bal_amt < 100) "
        "\n"
        "  ) "
    )
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
