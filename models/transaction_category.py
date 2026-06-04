from semantido import semantic_table
from semantido.generators.semantic_layer import PrivacyLevel
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from semantido.models.declarative_base import SemanticDeclarativeBase

@semantic_table(
    description="Reference table of transaction categories used to classify entries in txn_ledger. Supports a two-level hierarchy via parent_cat_id. Aligned with ISO 18245 Merchant Category Codes (MCC) where applicable.",
    synonyms=["category", "spending category", "transaction type", "merchant category", "spend classification"],
    sql_filters=["WHERE", "JOIN", "ORDER BY"],
    application_context=(
        "Join to transactions_ledger on cat_id to classify or filter transactions by category. "
        "Use is_debit_flg = TRUE to filter for spending categories and FALSE for income categories (e.g. salary, interest). "
        "Use parent_cat_id IS NULL to query only top-level categories. "
        "For hierarchical spend analysis, self-join on parent_cat_id."
    ),
)
class TransactionCategoryReference(SemanticDeclarativeBase):
    __tablename__ = "txn_cat_ref"
    __table_args__ = {"schema": "data_service"}

    cat_id = Column(Integer, primary_key=True, autoincrement=True)
    cat_id_description = "Primary key for the category."
    cat_id_privacy_level = PrivacyLevel.PUBLIC

    cat_cd = Column(String(15), nullable=False, unique=True)
    cat_cd_description = "Short code for the category (e.g. GROC, SALARY, ATM_WDL). Used in downstream categorisation logic and spend analytics."
    cat_cd_privacy_level = PrivacyLevel.PUBLIC
    cat_cd_example = ["GROC", "SALARY", "ATM_WDL", "DINING", "UTILITIES", "INTEREST"]

    cat_desc = Column(String(100), nullable=True)
    cat_desc_description = "Human-readable description of the category."
    cat_desc_privacy_level = PrivacyLevel.PUBLIC
    cat_desc_example = ["Groceries & Supermarkets", "Salary / Payroll Credit", "ATM Cash Withdrawal", None]

    is_debit_flg = Column(Boolean, nullable=False, server_default="true")
    is_debit_flg_description = "Indicates whether this category typically represents a debit (money out) transaction. TRUE = debit (e.g. groceries), FALSE = credit (e.g. salary, interest)."
    is_debit_flg_privacy_level = PrivacyLevel.PUBLIC
    is_debit_flg_example = [True, False]

    transactions = relationship("TransactionLedger", back_populates="category")

    def __repr__(self) -> str:
        return (
            f"<TransactionCategoryRef(cat_id={self.cat_id!r}, "
            f"cat_cd={self.cat_cd!r}, "
            f"cat_desc={self.cat_desc!r}, "
            f"is_debit_flg={self.is_debit_flg!r})>"
        )
