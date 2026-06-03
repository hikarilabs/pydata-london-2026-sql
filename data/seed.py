import asyncio
from datetime import date
from decimal import Decimal

from db.client import PostgresClient

# Import via the package so __init__.py runs and ALL models register
# with SemanticDeclarativeBase before any mapper configuration is triggered
import models  # noqa: F401

from models.products import ProductCatalog
from models.customers import Customer
from models.accounts import AccountInfo
from models.customer_account_map import CustomerAccountMap
from models.account_product_map import AccountProductMap
from models.transaction_category import TransactionCategoryReference
from models.transactions import TransactionLedger


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

PRODUCTS = [
    ProductCatalog(
        prod_cd="DEP-CURR-STD",
        prod_nm="Standard Current Account",
        prod_cat="DEPOSIT",
        prod_sub_cat="CURRENT",
        int_rate_pct=Decimal("0.1000"),
        fee_monthly_amt=Decimal("0.00"),
        ccy_cd="GBP",
    ),
    ProductCatalog(
        prod_cd="DEP-CURR-PRM",
        prod_nm="Premier Current Account",
        prod_cat="DEPOSIT",
        prod_sub_cat="CURRENT",
        int_rate_pct=Decimal("0.2500"),
        fee_monthly_amt=Decimal("0.00"),
        ccy_cd="GBP",
    ),
    ProductCatalog(
        prod_cd="DEP-SAV-EASY",
        prod_nm="Easy Access Savings",
        prod_cat="DEPOSIT",
        prod_sub_cat="SAVINGS",
        int_rate_pct=Decimal("3.5000"),
        fee_monthly_amt=Decimal("0.00"),
        ccy_cd="GBP",
    ),
    ProductCatalog(
        prod_cd="LN-BIZ-OVD",
        prod_nm="Business Overdraft Facility",
        prod_cat="LOAN",
        prod_sub_cat="OVERDRAFT",
        int_rate_pct=Decimal("8.5000"),
        fee_monthly_amt=Decimal("15.00"),
        ccy_cd="GBP",
    ),
    ProductCatalog(
        prod_cd="ADDON-DEBIT-STD",
        prod_nm="Standard Debit Card",
        prod_cat="CARD",
        prod_sub_cat="DEBIT",
        int_rate_pct=Decimal("0.0000"),
        fee_monthly_amt=Decimal("0.00"),
        ccy_cd="GBP",
    ),
    ProductCatalog(
        prod_cd="ADDON-CRED-RWD",
        prod_nm="Rewards Credit Card",
        prod_cat="CARD",
        prod_sub_cat="CREDIT",
        int_rate_pct=Decimal("22.9000"),
        fee_monthly_amt=Decimal("3.00"),
        ccy_cd="GBP",
    ),
]

CUSTOMERS = [
    Customer(
        cust_ref_no="CIF-001",
        f_name="Oliver",
        l_name="Hawthorne",
        cust_seg="RETAIL",
        kyc_stat="VERIFIED",
        prim_email="o.hawthorne@email.co.uk",
    ),
    Customer(
        cust_ref_no="CIF-002",
        f_name="Amelia",
        l_name="Patel",
        cust_seg="RETAIL",
        kyc_stat="VERIFIED",
        prim_email="a.patel@email.co.uk",
    ),
    Customer(
        cust_ref_no="CIF-003",
        f_name="Liam",
        l_name="Fitzgerald",
        cust_seg="HNW",
        kyc_stat="VERIFIED",
        prim_email="l.fitzgerald@email.ie",
    ),
    Customer(
        cust_ref_no="CIF-004",
        f_name="Isabella",
        l_name="Reyes",
        cust_seg="SME",
        kyc_stat="VERIFIED",
        prim_email="isabelle.r@reyesltd.com",
    ),
    Customer(
        cust_ref_no="CIF-005",
        f_name="Thomas",
        l_name="Obi",
        cust_seg="RETAIL",
        kyc_stat="VERIFIED",
        prim_email="t.obi@email.co.uk",
    ),
]

ACCOUNTS = [
    AccountInfo(
        acct_no="10000001",
        prod_id=1,
        acct_stat="ACTIVE",
        open_dt=date(2022, 1, 12),
        curr_bal_amt=Decimal("4250.00"),
        avail_bal_amt=Decimal("4250.00"),
        od_limit_amt=Decimal("500.00"),
        ccy_cd="GBP",
        last_txn_dt=date(2026, 5, 22),
    ),
    AccountInfo(
        acct_no="10000002",
        prod_id=1,
        acct_stat="ACTIVE",
        open_dt=date(2021, 11, 7),
        curr_bal_amt=Decimal("3100.00"),
        avail_bal_amt=Decimal("1600.00"),
        od_limit_amt=Decimal("200.00"),
        ccy_cd="GBP",
        last_txn_dt=date(2026, 5, 23),
    ),
    AccountInfo(
        acct_no="10000003",
        prod_id=2,
        acct_stat="ACTIVE",
        open_dt=date(2020, 6, 20),
        curr_bal_amt=Decimal("85400.00"),
        avail_bal_amt=Decimal("85400.00"),
        od_limit_amt=Decimal("2000.00"),
        ccy_cd="GBP",
        last_txn_dt=date(2026, 5, 23),
    ),
    AccountInfo(
        acct_no="10000004",
        prod_id=3,
        acct_stat="ACTIVE",
        open_dt=date(2019, 1, 8),
        curr_bal_amt=Decimal("52000.00"),
        avail_bal_amt=Decimal("52000.00"),
        od_limit_amt=Decimal("0.00"),
        ccy_cd="GBP",
        last_txn_dt=date(2026, 5, 20),
    ),
    AccountInfo(
        acct_no="10000005",
        prod_id=1,
        acct_stat="ACTIVE",
        open_dt=date(2022, 7, 31),
        curr_bal_amt=Decimal("2100.00"),
        avail_bal_amt=Decimal("850.00"),
        od_limit_amt=Decimal("300.00"),
        ccy_cd="GBP",
        last_txn_dt=date(2026, 5, 22),
    ),
    AccountInfo(
        acct_no="10000006",
        prod_id=1,
        acct_stat="ACTIVE",
        open_dt=date(2021, 4, 19),
        curr_bal_amt=Decimal("18900.00"),
        avail_bal_amt=Decimal("18900.00"),
        od_limit_amt=Decimal("1000.00"),
        ccy_cd="GBP",
        last_txn_dt=date(2026, 5, 22),
    ),
]

CUSTOMER_ACCOUNT_MAPS = [
    CustomerAccountMap(
        cust_id=1, acct_id=1, rel_typ="PRIMARY", eff_from_dt=date(2022, 1, 12)
    ),
    CustomerAccountMap(
        cust_id=2, acct_id=2, rel_typ="PRIMARY", eff_from_dt=date(2021, 11, 7)
    ),
    CustomerAccountMap(
        cust_id=3, acct_id=3, rel_typ="PRIMARY", eff_from_dt=date(2020, 6, 20)
    ),
    CustomerAccountMap(
        cust_id=3, acct_id=4, rel_typ="PRIMARY", eff_from_dt=date(2019, 1, 8)
    ),
    CustomerAccountMap(
        cust_id=5, acct_id=5, rel_typ="PRIMARY", eff_from_dt=date(2022, 7, 31)
    ),
    CustomerAccountMap(
        cust_id=4, acct_id=6, rel_typ="PRIMARY", eff_from_dt=date(2021, 4, 19)
    ),
]

ACCOUNT_PRODUCT_MAPS = [
    AccountProductMap(
        acct_id=1,
        prod_id=5,
        enrol_dt=date(2022, 1, 15),
        prov_status="ACTIVE",
        note_txt="Standard debit card — enrolled at account opening",
    ),
    AccountProductMap(
        acct_id=2,
        prod_id=5,
        enrol_dt=date(2021, 11, 10),
        prov_status="ACTIVE",
        note_txt="Standard debit card",
    ),
    AccountProductMap(
        acct_id=3,
        prod_id=6,
        enrol_dt=date(2020, 7, 1),
        prov_status="ACTIVE",
        note_txt="Rewards credit card — Premier customer",
    ),
    AccountProductMap(
        acct_id=4,
        prod_id=5,
        enrol_dt=date(2019, 1, 15),
        prov_status="ACTIVE",
        note_txt="Standard debit card",
    ),
    AccountProductMap(
        acct_id=5,
        prod_id=5,
        enrol_dt=date(2022, 8, 1),
        prov_status="ACTIVE",
        note_txt="Standard debit card",
    ),
    AccountProductMap(
        acct_id=6,
        prod_id=6,
        enrol_dt=date(2021, 5, 1),
        prov_status="ACTIVE",
        note_txt="Rewards credit card linked to SME account",
    ),
    AccountProductMap(
        acct_id=6,
        prod_id=4,
        enrol_dt=date(2022, 1, 1),
        prov_status="ACTIVE",
        note_txt="Business overdraft facility add-on",
    ),
]

TXN_CATEGORIES = [
    TransactionCategoryReference(
        cat_cd="SALARY", cat_desc="Salary / payroll credit", is_debit_flg=False
    ),
    TransactionCategoryReference(
        cat_cd="GROC", cat_desc="Groceries & supermarkets", is_debit_flg=True
    ),
    TransactionCategoryReference(
        cat_cd="UTIL", cat_desc="Utilities & bills", is_debit_flg=True
    ),
    TransactionCategoryReference(
        cat_cd="INTR", cat_desc="Interest credit", is_debit_flg=False
    ),
]

TRANSACTIONS = [
    # Account 1 — Oliver
    TransactionLedger(
        txn_ref="TXN-001",
        acct_id=1,
        cat_id=1,
        txn_typ="CREDIT",
        txn_dt=date(2026, 5, 1),
        amt=Decimal("3500.00"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("7750.00"),
        chan_cd="BACS",
        narr_txt="Salary May 2026",
    ),
    TransactionLedger(
        txn_ref="TXN-002",
        acct_id=1,
        cat_id=2,
        txn_typ="DEBIT",
        txn_dt=date(2026, 5, 3),
        amt=Decimal("125.40"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("7624.60"),
        chan_cd="POS",
        narr_txt="TESCO STORES 5892",
    ),
    TransactionLedger(
        txn_ref="TXN-003",
        acct_id=1,
        cat_id=3,
        txn_typ="DEBIT",
        txn_dt=date(2026, 5, 7),
        amt=Decimal("145.00"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("7479.60"),
        chan_cd="ONLINE",
        narr_txt="BG ENERGY DIRECT DD",
    ),
    TransactionLedger(
        txn_ref="TXN-004",
        acct_id=1,
        cat_id=2,
        txn_typ="DEBIT",
        txn_dt=date(2026, 5, 12),
        amt=Decimal("87.50"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("7392.10"),
        chan_cd="POS",
        narr_txt="DISHOOM CARNABY ST",
    ),
    # Account 2 — Amelia
    TransactionLedger(
        txn_ref="TXN-005",
        acct_id=2,
        cat_id=1,
        txn_typ="CREDIT",
        txn_dt=date(2026, 5, 1),
        amt=Decimal("2800.00"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("4340.75"),
        chan_cd="BACS",
        narr_txt="Salary May 2026 — NHS",
    ),
    TransactionLedger(
        txn_ref="TXN-006",
        acct_id=2,
        cat_id=2,
        txn_typ="DEBIT",
        txn_dt=date(2026, 5, 4),
        amt=Decimal("88.20"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("4252.55"),
        chan_cd="POS",
        narr_txt="MORRISONS DIDSBURY",
    ),
    TransactionLedger(
        txn_ref="TXN-007",
        acct_id=2,
        cat_id=3,
        txn_typ="DEBIT",
        txn_dt=date(2026, 5, 6),
        amt=Decimal("112.00"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("4140.55"),
        chan_cd="ONLINE",
        narr_txt="OCTOPUS ENRGY DD",
    ),
    # Account 3 — Liam premier current
    TransactionLedger(
        txn_ref="TXN-008",
        acct_id=3,
        cat_id=1,
        txn_typ="CREDIT",
        txn_dt=date(2026, 5, 1),
        amt=Decimal("18000.00"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("103400.00"),
        chan_cd="BACS",
        narr_txt="Management fee Q1 Soren Capital",
    ),
    TransactionLedger(
        txn_ref="TXN-009",
        acct_id=3,
        cat_id=None,
        txn_typ="DEBIT",
        txn_dt=date(2026, 5, 3),
        amt=Decimal("15000.00"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("88400.00"),
        chan_cd="ONLINE",
        narr_txt="Transfer to savings 10000004",
    ),
    # Account 4 — Liam savings
    TransactionLedger(
        txn_ref="TXN-010",
        acct_id=4,
        cat_id=None,
        txn_typ="CREDIT",
        txn_dt=date(2026, 5, 3),
        amt=Decimal("15000.00"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("67000.00"),
        chan_cd="ONLINE",
        narr_txt="Transfer from current 10000003",
    ),
    TransactionLedger(
        txn_ref="TXN-011",
        acct_id=4,
        cat_id=4,
        txn_typ="CREDIT",
        txn_dt=date(2026, 5, 1),
        amt=Decimal("151.04"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("52151.04"),
        chan_cd="BACS",
        narr_txt="Interest Easy Access Apr 2026",
    ),
    # Account 5 — Thomas
    TransactionLedger(
        txn_ref="TXN-012",
        acct_id=5,
        cat_id=1,
        txn_typ="CREDIT",
        txn_dt=date(2026, 5, 1),
        amt=Decimal("2200.00"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("4300.00"),
        chan_cd="BACS",
        narr_txt="Salary May 2026 Obi Consulting",
    ),
    TransactionLedger(
        txn_ref="TXN-013",
        acct_id=5,
        cat_id=2,
        txn_typ="DEBIT",
        txn_dt=date(2026, 5, 5),
        amt=Decimal("64.30"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("4235.70"),
        chan_cd="POS",
        narr_txt="ALDI STORES TRAFFORD",
    ),
    TransactionLedger(
        txn_ref="TXN-014",
        acct_id=5,
        cat_id=2,
        txn_typ="DEBIT",
        txn_dt=date(2026, 5, 8),
        amt=Decimal("42.80"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("4192.90"),
        chan_cd="POS",
        narr_txt="NANDOS PICCADILLY GDNS",
    ),
    # Account 6 — Isabella / Reyes Ltd (FM-1 account)
    TransactionLedger(
        txn_ref="TXN-015",
        acct_id=6,
        cat_id=1,
        txn_typ="CREDIT",
        txn_dt=date(2026, 5, 1),
        amt=Decimal("9500.00"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("28400.00"),
        chan_cd="CHAPS",
        narr_txt="Reyes Consulting Ltd May retainer",
    ),
    TransactionLedger(
        txn_ref="TXN-016",
        acct_id=6,
        cat_id=3,
        txn_typ="DEBIT",
        txn_dt=date(2026, 5, 10),
        amt=Decimal("1200.00"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("27200.00"),
        chan_cd="ONLINE",
        narr_txt="AWS AMAZON WEB SERVICES",
    ),
    TransactionLedger(
        txn_ref="TXN-017",
        acct_id=6,
        cat_id=3,
        txn_typ="DEBIT",
        txn_dt=date(2026, 5, 12),
        amt=Decimal("450.00"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("26750.00"),
        chan_cd="ONLINE",
        narr_txt="MSFT AZURE SUBSCRIPTION",
    ),
    TransactionLedger(
        txn_ref="TXN-018",
        acct_id=6,
        cat_id=None,
        txn_typ="FEE",
        txn_dt=date(2026, 5, 1),
        amt=Decimal("15.00"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("26735.00"),
        chan_cd="BACS",
        narr_txt="Business overdraft monthly fee",
    ),
    TransactionLedger(
        txn_ref="TXN-019",
        acct_id=6,
        cat_id=3,
        txn_typ="CREDIT",
        txn_dt=date(2026, 5, 13),
        amt=Decimal("450.00"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("27185.00"),
        chan_cd="ONLINE",
        narr_txt="Reversal — MSFT duplicate charge",
    ),
    TransactionLedger(
        txn_ref="TXN-020",
        acct_id=6,
        cat_id=None,
        txn_typ="DEBIT",
        txn_dt=date(2026, 5, 18),
        amt=Decimal("750.00"),
        ccy_cd="GBP",
        bal_after_amt=Decimal("26435.00"),
        chan_cd="ONLINE",
        narr_txt="HMRC VAT Q1 2026",
    ),
]


# ---------------------------------------------------------------------------
# Seed runner
# ---------------------------------------------------------------------------


async def seed():
    client = PostgresClient.from_env(default_schema="data_service")

    try:
        async with client.session(schema="data_service") as session:
            # Insert in FK-dependency order
            for batch in [
                PRODUCTS,
                CUSTOMERS,
                ACCOUNTS,
                TXN_CATEGORIES,
                CUSTOMER_ACCOUNT_MAPS,
                ACCOUNT_PRODUCT_MAPS,
                TRANSACTIONS,
            ]:
                session.add_all(batch)
                await session.flush()  # resolve IDs before the next FK-dependent batch

            await session.commit()
            print("✅ Seed data inserted successfully.")

    except Exception as e:
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(seed())
