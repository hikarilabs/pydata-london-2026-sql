from semantido import semantic_table
from semantido.generators.semantic_layer import PrivacyLevel
from sqlalchemy import Column, Integer, String, Numeric, Boolean, CHAR
from sqlalchemy.orm import relationship
from semantido.models.declarative_base import SemanticDeclarativeBase


@semantic_table(
    description=(
        "Master list of bankable products. prod_cat distinguishes primary "
        "account products (DEPOSIT, LOAN) from add-on features (CARD) that "
        "are enrolled via acct_prod_map. For balance aggregation by product, "
        "join directly from acct_info via acct_info.prod_id — this reflects "
        "each account's primary product and does not fan out."
    ),
    synonyms=[
        "product",
        "savings account",
        "ISA",
        "mortgage",
        "loan",
        "credit card",
        "debit card",
        "fixed bond",
        "current account product",
    ],
    sql_filters=["WHERE", "JOIN", "ORDER BY"],
    application_context=(
        "Join to acct_info on prod_id to get the product associated with an account. "
        "Filter by is_avail_flg = TRUE for products currently available for sale. "
        "Use int_rate_pct for the product default rate — check acct_info.int_rate_pct first as it may be overridden at account level. "
        "Use fee_monthly_amt for the default monthly fee."
    ),
)
class ProductCatalog(SemanticDeclarativeBase):
    __tablename__ = "products"
    __table_args__ = {"schema": "data_service"}

    prod_id = Column(Integer, primary_key=True, autoincrement=True)
    prod_id_description = "Primary key for the product."
    prod_id_privacy_level = PrivacyLevel.PUBLIC

    prod_cd = Column(String(20), nullable=False, unique=True)
    prod_cd_description = (
        "Short product code for filtering (e.g. 'ADDON-CRED-RWD', "
        "'LN-BIZ-OVD'). Use in WHERE clauses to target specific products."
    )
    prod_cd_privacy_level = PrivacyLevel.PUBLIC
    prod_cd_example = ["DEP-SAV-ISA", "LN-MORT-RES", "CARD-CREDIT-RWD"]

    prod_nm = Column(String(100), nullable=False)
    prod_nm_description = "Full marketing / display name of the product."
    prod_nm_privacy_level = PrivacyLevel.PUBLIC
    prod_nm_example = [
        "Instant Access Saver",
        "Residential Mortgage",
        "Rewards Credit Card",
    ]

    prod_cat = Column(String(20), nullable=False)  # DEPOSIT, LOAN, CARD
    prod_cat_description = (
        "Top-level product category. Values: DEPOSIT, LOAN, CARD. "
        "Use for GROUP BY in balance-by-category queries. "
        "When reached via acct_info.prod_id, one row per account — safe. "
        "When reached via acct_prod_map, multiple rows per account — "
        "see acct_prod_map warning."
    )
    prod_cat_privacy_level = PrivacyLevel.PUBLIC
    prod_cat_example = ["DEPOSIT", "LOAN", "CARD", "INVEST"]

    prod_sub_cat = Column(String(20), nullable=True)
    prod_sub_cat_description = "Secondary classification within the category (e.g. CURRENT, ISA, MORTGAGE, OVERDRAFT, DEBIT, CREDIT)."
    prod_sub_cat_privacy_level = PrivacyLevel.PUBLIC
    prod_sub_cat_example = [
        "CURRENT",
        "ISA",
        "MORTGAGE",
        "OVERDRAFT",
        "DEBIT",
        "CREDIT",
        None,
    ]

    int_rate_pct = Column(Numeric(7, 4), nullable=True)
    int_rate_pct_description = "Annual interest rate as a percentage (e.g. 4.1000 = 4.10% AER). For lending products this is the APR; for deposits, the AER. NULL for non-interest-bearing products."
    int_rate_pct_privacy_level = PrivacyLevel.PUBLIC
    int_rate_pct_example = [4.1000, 6.9900, 0.1000, None]

    fee_monthly_amt = Column(Numeric(10, 2), nullable=True, server_default="0")
    fee_monthly_amt_description = "Fixed monthly maintenance fee charged to the account. Zero for no-fee products."
    fee_monthly_amt_privacy_level = PrivacyLevel.PUBLIC
    fee_monthly_amt_example = [0.00, 9.99, 15.00]

    ccy_cd = Column(CHAR(3), nullable=True, server_default="GBP")
    ccy_cd_description = "Default currency for this product (ISO 4217)."
    ccy_cd_privacy_level = PrivacyLevel.PUBLIC
    ccy_cd_example = ["GBP", "EUR", "USD"]

    is_avail_flg = Column(Boolean, nullable=False, server_default="true")
    is_avail_flg_description = "Whether this product is currently available for new applications. FALSE = retired or temporarily withdrawn."
    is_avail_flg_privacy_level = PrivacyLevel.PUBLIC
    is_avail_flg_example = [True, False]

    account_maps = relationship("AccountProductMap", back_populates="product")

    def __repr__(self) -> str:
        return (
            f"<ProdCatalog(prod_id={self.prod_id!r}, "
            f"prod_cd={self.prod_cd!r}, "
            f"prod_nm={self.prod_nm!r}, "
            f"prod_cat={self.prod_cat!r})>"
        )
