
CREATE TABLE currency_pair (
id SMALLINT NOT NULL AUTO_INCREMENT,
name CHAR(35) NOT NULL UNIQUE,
PRIMARY KEY (id)
);

CREATE TABLE exchange (
id SMALLINT NOT NULL AUTO_INCREMENT,
name CHAR(35) NOT NULL UNIQUE,
PRIMARY KEY(id)
);

CREATE TABLE price_type (
id SMALLINT NOT NULL AUTO_INCREMENT,
name CHAR(30) NOT NULL UNIQUE,
PRIMARY KEY(id)
);


CREATE TABLE  coin_price (
date_time_sec BIGINT NOT NULL,
exchange_id SMALLINT NOT NULL,
currency_pair_id SMALLINT NOT NULL,
price DOUBLE PRECISION(22,8) NOT NULL,
date_time DATETIME NOT NULL,
price_type_id SMALLINT NOT NULL,
PRIMARY KEY (date_time_sec, exchange_id, currency_pair_id ),
FOREIGN KEY (exchange_id) REFERENCES exchange (id),
FOREIGN KEY (currency_pair_id) REFERENCES currency_pair (id),
FOREIGN KEY (price_type_id) REFERENCES price_type (id)
);


insert into currency_pair(name) values
("btc_mxn"),("eth_mxn"),("xrp_mxn"),("ltc_mxn"),

("btc_usd"),("eth_usd"),("xrp_usd"),("iot_usd"),("ltc_usd"),("bch_usd"),("dsh_usd"),

("eth_btc"),("ltc_btc"),("bnb_btc"),("neo_btc"),("bcc_btc"),("gas_btc"),("hsr_btc"),
("mco_btc"),("wtc_btc"),("lrc_btc"),("qtum_btc"),("yoyo_btc"),("omg_btc"),("zrx_btc"),
("strat_btc"),("sngls_btc"),("bqx_btc"),("knc_btc"),("fun_btc"),("snm_btc"),("iota_btc"),
("link_btc"),("xvg_btc"),("ctr_btc"),("salt_btc"),("mda_btc"),("mtl_btc"),("sub_btc"),
("eos_btc"),("snt_btc"),("etc_btc"),("mth_btc"),("eng_btc"),("dnt_btc"),("zec_btc"),
("bnt_btc"),("ast_btc"),("dash_btc"),("oax_btc"),("icn_btc"),("btg_btc"),("evx_btc"),
("req_btc"),("vib_btc"),("trx_btc"),("powr_btc"),("ark_btc"),("xrp_btc"),("mod_btc"),
("enj_btc"),("storj_btc"),("ven_btc"),("kmd_btc"),("rcn_btc"),("nuls_btc"),("rdn_btc"),
("xmr_btc"),("dlt_btc"),("amb_btc"),("bat_btc"),("bcpt_btc"),("arn_btc"),("gvt_btc"),
("cdt_btc"),("gxs_btc"),("poe_btc"),("qsp_btc"),("bts_btc"),("xzc_btc"),("lsk_btc"),
("tnt_btc"),("fuel_btc"),("mana_btc"),("bcd_btc"),("dgd_btc"),("adx_btc"),("ada_btc"),
("ppt_btc"),("cmt_btc"),("xlm_btc"),("cnd_btc"),("lend_btc"),("wabi_btc"),("tnb_btc"),
("waves_btc"),("gto_btc"),("icx_btc"),("ost_btc"),("elf_btc"),("aion_btc"),("nebl_btc"),
("brd_btc"),("edo_btc"),("wings_btc"),("nav_btc"),("lun_btc"),("trig_btc"),("appc_btc"),
("vibe_btc");


insert into price_type(name) values("last");

insert into exchange(name) values ("bitso"),("bitfinex"), ("binance"), ("poloniex"), ("hitbtc"), ("cex.io");

insert into exchange(name) values ("bitstamp"), ("bittrex");





