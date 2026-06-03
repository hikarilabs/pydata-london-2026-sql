-- =============================================================================
-- 1. customer
-- =============================================================================
CREATE TABLE data_service.customer (
	cust_id SERIAL NOT NULL, 
	cust_ref_no VARCHAR(20) NOT NULL, 
	f_name VARCHAR(80) NOT NULL, 
	l_name VARCHAR(80) NOT NULL, 
	cust_seg VARCHAR(20), 
	kyc_stat VARCHAR(10), 
	prim_email VARCHAR(150), 
	created_ts TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_ts TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (cust_id), 
	UNIQUE (cust_ref_no)
)


-- =============================================================================
-- 2. products
-- =============================================================================
CREATE TABLE data_service.products (
	prod_id SERIAL NOT NULL, 
	prod_cd VARCHAR(20) NOT NULL, 
	prod_nm VARCHAR(100) NOT NULL, 
	prod_cat VARCHAR(20) NOT NULL, 
	prod_sub_cat VARCHAR(20), 
	int_rate_pct NUMERIC(7, 4), 
	fee_monthly_amt NUMERIC(10, 2) DEFAULT '0', 
	ccy_cd CHAR(3) DEFAULT 'GBP', 
	is_avail_flg BOOLEAN DEFAULT 'true' NOT NULL, 
	PRIMARY KEY (prod_id), 
	UNIQUE (prod_cd)
)


-- =============================================================================
-- 3. txn_cat_ref
-- =============================================================================
CREATE TABLE data_service.txn_cat_ref (
	cat_id SERIAL NOT NULL, 
	cat_cd VARCHAR(15) NOT NULL, 
	cat_desc VARCHAR(100), 
	is_debit_flg BOOLEAN DEFAULT 'true' NOT NULL, 
	PRIMARY KEY (cat_id), 
	UNIQUE (cat_cd)
)


-- =============================================================================
-- 4. acct_info
-- =============================================================================
CREATE TABLE data_service.acct_info (
	acct_id SERIAL NOT NULL, 
	acct_no VARCHAR(20) NOT NULL, 
	prod_id INTEGER NOT NULL, 
	acct_stat VARCHAR(10) DEFAULT 'ACTIVE' NOT NULL, 
	open_dt DATE NOT NULL, 
	curr_bal_amt NUMERIC(18, 2) DEFAULT '0' NOT NULL, 
	avail_bal_amt NUMERIC(18, 2) DEFAULT '0' NOT NULL, 
	od_limit_amt NUMERIC(14, 2) DEFAULT '0', 
	ccy_cd CHAR(3) DEFAULT 'GBP' NOT NULL, 
	last_txn_dt DATE, 
	created_ts TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (acct_id), 
	UNIQUE (acct_no), 
	FOREIGN KEY(prod_id) REFERENCES data_service.products (prod_id)
)


-- =============================================================================
-- 5. acct_prod_map
-- =============================================================================
CREATE TABLE data_service.acct_prod_map (
	map_id SERIAL NOT NULL, 
	acct_id INTEGER NOT NULL, 
	prod_id INTEGER NOT NULL, 
	enrol_dt DATE DEFAULT CURRENT_DATE NOT NULL, 
	prov_status VARCHAR(10) DEFAULT 'ACTIVE', 
	note_txt TEXT, 
	PRIMARY KEY (map_id), 
	CONSTRAINT uq_acct_prod UNIQUE (acct_id, prod_id), 
	FOREIGN KEY(acct_id) REFERENCES data_service.acct_info (acct_id), 
	FOREIGN KEY(prod_id) REFERENCES data_service.products (prod_id)
)


-- =============================================================================
-- 6. cust_acct_map
-- =============================================================================
CREATE TABLE data_service.cust_acct_map (
	map_id SERIAL NOT NULL, 
	cust_id INTEGER NOT NULL, 
	acct_id INTEGER NOT NULL, 
	rel_typ VARCHAR(20) DEFAULT 'PRIMARY' NOT NULL, 
	eff_from_dt DATE DEFAULT CURRENT_DATE NOT NULL, 
	eff_to_dt DATE, 
	PRIMARY KEY (map_id), 
	CONSTRAINT uq_cust_acct_rel UNIQUE (cust_id, acct_id, rel_typ), 
	FOREIGN KEY(cust_id) REFERENCES data_service.customer (cust_id), 
	FOREIGN KEY(acct_id) REFERENCES data_service.acct_info (acct_id)
)


-- =============================================================================
-- 7. transactions_ledger
-- =============================================================================
CREATE TABLE data_service.transactions_ledger (
	txn_id BIGSERIAL NOT NULL, 
	txn_ref VARCHAR(30) NOT NULL, 
	acct_id INTEGER NOT NULL, 
	cat_id INTEGER, 
	txn_typ VARCHAR(10) NOT NULL, 
	txn_dt DATE NOT NULL, 
	amt NUMERIC(18, 2) NOT NULL, 
	ccy_cd CHAR(3) DEFAULT 'GBP' NOT NULL, 
	bal_after_amt NUMERIC(18, 2), 
	chan_cd VARCHAR(10), 
	narr_txt VARCHAR(255), 
	created_ts TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (txn_id), 
	CONSTRAINT chk_txn_amt_positive CHECK (amt > 0), 
	UNIQUE (txn_ref), 
	FOREIGN KEY(acct_id) REFERENCES data_service.acct_info (acct_id), 
	FOREIGN KEY(cat_id) REFERENCES data_service.txn_cat_ref (cat_id)
)

