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
    description="The central financial ledger. Every monetary movement against an account — credits, debits, fees, interest, and reversals — is recorded here. This is the most write-intensive table in the schema.",
    synonyms=["transaction", "payment", "debit", "credit", "transfer", "statement entry", "spend", "income", "fee", "interest", "reversal"],
    sql_filters=["WHERE", "JOIN", "ORDER BY", "GROUP BY"],
    application_context=(
        "Always reach this table via data_service.acct_info JOIN data_service.cust_acct_map to scope to the authenticated customer. "
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
    txn_id_description = "Surrogate primary key. Uses BIGSERIAL to support high transaction volumes."
    txn_id_privacy_level = PrivacyLevel.PUBLIC

    txn_ref = Column(String(30), nullable=False, unique=True)
    txn_ref_description = "Business-facing unique transaction reference (e.g. TXN-2026-0001). Surfaced on statements and in dispute resolution."
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

    txn_typ = Column(String(10), nullable=False)  # DEBIT, CREDIT, FEE, INTEREST, REVERSAL
    txn_typ_description = "Transaction type. DEBIT = money out, CREDIT = money in, REVERSAL = correction of a prior posting, FEE = product or service fee, INTEREST = interest credit or debit."
    txn_typ_privacy_level = PrivacyLevel.PUBLIC
    txn_typ_example = ["DEBIT", "CREDIT", "REVERSAL", "FEE", "INTEREST"]

    txn_dt = Column(Date, nullable=False)
    txn_dt_description = "The business date on which the transaction occurred (as known to the customer). May differ from val_dt for cross-border or delayed-clearing transactions."
    txn_dt_privacy_level = PrivacyLevel.PUBLIC
    txn_dt_example = ["2026-05-01", "2026-04-30"]

    amt = Column(Numeric(18, 2), nullable=False)
    amt_description = "Transaction amount in the account's currency. Always stored as a positive number; direction is conveyed by txn_typ."
    amt_privacy_level = PrivacyLevel.CONFIDENTIAL
    amt_example = [49.99, 1500.00, 0.25]

    ccy_cd = Column(CHAR(3), nullable=False, server_default="GBP")
    ccy_cd_description = "Currency of the transaction (ISO 4217). Should match acct_info.ccy_cd for domestic transactions; may differ for foreign currency card transactions."
    ccy_cd_privacy_level = PrivacyLevel.PUBLIC
    ccy_cd_example = ["GBP", "EUR", "USD"]

    bal_after_amt = Column(Numeric(18, 2), nullable=True)
    bal_after_amt_description = "Ledger balance on the account immediately after this transaction was posted. Denormalised for statement generation performance."
    bal_after_amt_privacy_level = PrivacyLevel.CONFIDENTIAL
    bal_after_amt_example = [1200.01, -45.00, None]

    chan_cd = Column(String(10), nullable=True)  # ATM, MOBILE, ONLINE, POS, BACS, CHAPS
    chan_cd_description = "Channel through which the transaction was initiated. ATM = cash machine, MOBILE = mobile app, BRANCH = in-branch teller, ONLINE = internet banking, POS = point-of-sale terminal, BACS = BACS direct credit/debit, CHAPS = CHAPS same-day payment."
    chan_cd_privacy_level = PrivacyLevel.PUBLIC
    chan_cd_example = ["ATM", "MOBILE", "BRANCH", "ONLINE", "POS", "BACS", "CHAPS", None]

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
