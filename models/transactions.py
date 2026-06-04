from semantido import semantic_table
from semantido.generators.semantic_layer import PrivacyLevel
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Numeric,
    Date,
    DateTime,
    CHAR,
    ForeignKey,
    CheckConstraint,
    func,
)
from typing import Optional

from sqlalchemy.orm import relationship
from semantido.models.declarative_base import SemanticDeclarativeBase


@semantic_table(
    description=(
        "Full transaction ledger. Every monetary movement against an account. "
        "SIGN CONVENTION: amt is always stored as a positive number — direction "
        "is encoded in txn_typ, not in the sign of amt. "
        "SUM(amt) without a signed expression or txn_typ filter cannot represent "
        "net position and will always return a large positive number."
    ),
    synonyms=[
        "transaction",
        "payment",
        "debit",
        "credit",
        "transfer",
        "statement entry",
        "spend",
        "income",
        "fee",
        "interest",
        "reversal",
    ],
    sql_filters=["WHERE", "JOIN", "ORDER BY", "GROUP BY"],
    application_context=(
        "Reach via cust_acct_map only when customer-level scoping is required. For portfolio-level transaction analysis (channel totals, net flow by account), join transactions_ledger directly to acct_info without the customer bridge."
        "Use txn_dt for customer-facing date filtering (e.g. 'last month'). "
        "amt is always positive — use txn_typ to determine direction (DEBIT = money out, CREDIT = money in). "
        "Join to txn_cat_ref on cat_id for category-based spend analysis. "
        "For spend totals exclude REVERSAL entries or handle them explicitly. "
        "Use chan_cd to filter by channel (e.g. ATM, MOBILE, POS)."
    ),
)
class TransactionLedger(SemanticDeclarativeBase):
    __tablename__ = "transactions_ledger"
    __table_args__ = (
        CheckConstraint("amt > 0", name="chk_txn_amt_positive"),
        {"schema": "data_service"},
    )

    txn_id = Column(BigInteger, primary_key=True, autoincrement=True)
    txn_id_description = (
        "Surrogate primary key. Uses BIGSERIAL to support high transaction volumes."
    )
    txn_id_privacy_level = PrivacyLevel.PUBLIC

    txn_ref = Column(String(30), nullable=False, unique=True)
    txn_ref_description = (
        "Business-facing transaction reference. Use in SELECT output "
        "to identify a transaction — do not expose the surrogate txn_id."
    )
    txn_ref_privacy_level = PrivacyLevel.PUBLIC
    txn_ref_example = ["TXN-2026-0001", "TXN-2026-9842"]

    acct_id = Column(
        Integer, ForeignKey("data_service.acct_info.acct_id"), nullable=False
    )
    acct_id_description = "Foreign key to data_service.acct_info.acct_id. The account this transaction is posted against."
    acct_id_privacy_level = PrivacyLevel.PUBLIC

    cat_id: Optional[int] = Column(
        Integer, ForeignKey("data_service.txn_cat_ref.cat_id"), nullable=True
    )
    cat_id_description = "Foreign key to data_service.txn_cat_ref.cat_id. The spending or income category assigned to this transaction. May be NULL for uncategorised entries."
    cat_id_privacy_level = PrivacyLevel.PUBLIC
    cat_id_example = [3, None]

    txn_typ = Column(
        String(10), nullable=False
    )  # DEBIT, CREDIT, FEE, INTEREST, REVERSAL
    txn_typ_description = (
        "Transaction direction and type. "
        "Values: CREDIT (money in), DEBIT (money out), "
        "INTEREST (money in — interest credit), FEE (money out — charges). "
        "Always include in WHERE or CASE expressions alongside amt. "
        "CREDIT and INTEREST are positive contributions; "
        "DEBIT and FEE are negative contributions."
    )
    txn_typ_privacy_level = PrivacyLevel.PUBLIC
    txn_typ_example = ["DEBIT", "CREDIT", "REVERSAL", "FEE", "INTEREST"]

    txn_dt = Column(Date, nullable=False)
    txn_dt_description = "The business date on which the transaction occurred (as known to the customer). May differ from val_dt for cross-border or delayed-clearing transactions."
    txn_dt_privacy_level = PrivacyLevel.PUBLIC
    txn_dt_example = ["2026-05-01", "2026-04-30"]

    amt = Column(Numeric(18, 2), nullable=False)
    amt_description = (
        "Transaction amount. Always positive — see txn_typ for direction. "
        "NEVER use SUM(amt) for net flow or balance change. "
        "For net flow: SUM(CASE WHEN txn_typ IN ('CREDIT','INTEREST') "
        "THEN amt ELSE -amt END). "
        "For outflows only: SUM(amt) WHERE txn_typ IN ('DEBIT','FEE'). "
        "For inflows only: SUM(amt) WHERE txn_typ IN ('CREDIT','INTEREST')."
    )
    amt_privacy_level = PrivacyLevel.CONFIDENTIAL
    amt_example = [49.99, 1500.00, 0.25]

    ccy_cd = Column(CHAR(3), nullable=False, server_default="GBP")
    ccy_cd_description = "Currency of the transaction (ISO 4217). Should match acct_info.ccy_cd for domestic transactions; may differ for foreign currency card transactions."
    ccy_cd_privacy_level = PrivacyLevel.PUBLIC
    ccy_cd_example = ["GBP", "EUR", "USD"]

    bal_after_amt = Column(Numeric(18, 2), nullable=True)
    bal_after_amt_description = (
        "Stored running balance after this transaction was posted. "
        "Use this column for running-balance display — do not recompute "
        "via a window SUM(amt) OVER (...) unless cross-checking, and "
        "always use the signed expression in that case."
    )
    bal_after_amt_privacy_level = PrivacyLevel.CONFIDENTIAL
    bal_after_amt_example = [1200.01, -45.00, None]

    chan_cd = Column(String(10), nullable=True)  # ATM, MOBILE, ONLINE, POS, BACS, CHAPS
    chan_cd_description = (
        "Transaction channel. Values: ATM, MOBILE, ONLINE, POS, "
        "BACS, CHAPS, BRANCH. Use in GROUP BY for channel analysis."
    )
    chan_cd_privacy_level = PrivacyLevel.PUBLIC
    chan_cd_example = [
        "ATM",
        "MOBILE",
        "BRANCH",
        "ONLINE",
        "POS",
        "BACS",
        "CHAPS",
        None,
    ]

    narr_txt = Column(String(255), nullable=True)
    narr_txt_description = "Free-text transaction narrative as it appears on the customer's statement. Often sourced verbatim from the originating payment message."
    narr_txt_privacy_level = PrivacyLevel.PUBLIC
    narr_txt_example = ["TESCO STORES 1234 LONDON", "SALARY MAY 2026", None]

    created_ts = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_ts_description = "Record creation timestamp."
    created_ts_privacy_level = PrivacyLevel.PUBLIC

    account = relationship("AccountInfo", back_populates="transactions")
    category = relationship(
        "TransactionCategoryReference", back_populates="transactions"
    )

    def __repr__(self) -> str:
        return (
            f"<TransactionLedger(txn_id={self.txn_id!r}, "
            f"txn_ref={self.txn_ref!r}, "
            f"txn_typ={self.txn_typ!r}, "
            f"amt={self.amt!r})>"
        )
