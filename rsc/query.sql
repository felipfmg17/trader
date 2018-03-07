SELECT a.date_time_sec as Seconds, a.date_time as Date, b.name as "Currency Pair" , c.name as Exchange , a.price as Price
FROM coin_price as a
JOIN currency_pair as b
ON a.currency_pair_id = b.id
JOIN exchange as c
ON a.exchange_id = c.id
WHERE c.name = 'bitso'
AND b.name = 'xrp_mxn'
AND a.date_time_sec > 1515307382
AND a.date_time_sec < 1515912230 ;


SELECT count(*)
FROM coin_price as a
JOIN currency_pair as b
ON a.currency_pair_id = b.id
JOIN exchange as c
ON a.exchange_id = c.id
WHERE c.name = 'bitso'
AND b.name = 'xrp_mxn';


DELETE FROM coin_price 
WHERE exists
( 	SELECT * FROM  currency_pair 
	WHERE coin_price.currency_pair_id=currency_pair.id
	AND currency_pair.name = 'poe_btc' );



select count(*) from coin_price;


SELECT a.date_time_sec as Seconds, a.date_time as Date, b.name as "Currency Pair" , c.name as Exchange , a.price as Price
FROM coin_price as a
JOIN currency_pair as b
ON a.currency_pair_id = b.id
JOIN exchange as c
ON a.exchange_id = c.id
WHERE c.name = 'bitso'
AND b.name = 'xrp_mxn';


SELECT a.date_time_sec as Seconds, a.date_time as Date, b.name as "Currency Pair" , c.name as Exchange , a.price as Price
FROM coin_price as a
JOIN currency_pair as b
ON a.currency_pair_id = b.id
JOIN exchange as c
ON a.exchange_id = c.id
WHERE c.name = 'binance'
AND b.name = 'poe_btc';


SELECT * FROM (
SELECT a.date_time_sec as Seconds, a.date_time as Date, b.name as "Currency Pair" , c.name as Exchange , a.price as Price
FROM coin_price as a
JOIN currency_pair as b
ON a.currency_pair_id = b.id
JOIN exchange as c
ON a.exchange_id = c.id
WHERE c.name = 'bitfinex'
AND b.name = 'xrp_usd'
ORDER BY Seconds DESC
LIMIT 10 ) sub
ORDER BY Seconds ASC;

SELECT Price  FROM (
SELECT * FROM (
SELECT  a.price as Price, a.date_time_sec as Seconds
FROM coin_price as a
JOIN currency_pair as b
ON a.currency_pair_id = b.id
JOIN exchange as c
ON a.exchange_id = c.id
WHERE c.name = 'bitfinex'
AND b.name = 'xrp_usd'
ORDER BY a.date_time_sec DESC
LIMIT 10 ) sub
ORDER BY Seconds ASC) sub2;




SELECT a.date_time_sec as Seconds, a.date_time as Date, b.name as "Currency Pair" , c.name as Exchange , a.price as Price
FROM coin_price as a
JOIN currency_pair as b
ON a.currency_pair_id = b.id
JOIN exchange as c
ON a.exchange_id = c.id
WHERE c.name = 'bitfinex'
AND b.name = 'xrp_usd';


SELECT a.date_time_sec as Seconds, a.date_time as Date, b.name as "Currency Pair" , c.name as Exchange , a.price as Price
FROM coin_price as a
JOIN currency_pair as b
ON a.currency_pair_id = b.id
JOIN exchange as c
ON a.exchange_id = c.id
WHERE c.name = 'bitfinex'
AND b.name = 'xrp_usd'
AND a.date_time_sec > 1515912153;


SELECT a.date_time_sec as Seconds, a.date_time as Date, b.name as "Currency Pair" , c.name as Exchange , a.price as Price
FROM coin_price as a
JOIN currency_pair as b
ON a.currency_pair_id = b.id
JOIN exchange as c
ON a.exchange_id = c.id
WHERE c.name = 'binance'
AND b.name = 'vibe_btc';


SELECT a.date_time_sec as Seconds, a.date_time as Date, b.name as "Currency Pair" , c.name as Exchange , a.price as Price
FROM coin_price as a
JOIN currency_pair as b
ON a.currency_pair_id = b.id
JOIN exchange as c
ON a.exchange_id = c.id
WHERE c.name = 'bitso'
AND b.name = 'xrp_mxn'
AND a.date_time > '2018-01-07 12:00:00'
AND a.date_time < '2018-01-08 12:00:00';

SELECT a.date_time_sec as Seconds, a.date_time as Date, b.name as "Currency Pair" , c.name as Exchange , a.price as Price
FROM coin_price as a
JOIN currency_pair as b
ON a.currency_pair_id = b.id
JOIN exchange as c
ON a.exchange_id = c.id
WHERE c.name = 'bitso'
AND b.name = 'xrp_mxn'
AND a.date_time_sec > 1515307382
AND a.date_time_sec < 1515912230
ORDER BY  a.date_time_sec ASC;