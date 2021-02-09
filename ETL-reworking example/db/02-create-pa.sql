SET search_path TO pa, public;

/*
    REFERENCE TABLES
*/

DROP TABLE IF EXISTS payment_types CASCADE;
CREATE TABLE payment_types (
    payment_type integer PRIMARY KEY,
    description text
);

INSERT INTO payment_types(payment_type, description) 
VALUES
(1, 'CREDIT CARD'),
(2, 'CASH'),
(3, 'NO CHARGE'),
(4, 'DISPUTE'),
(5, 'UNKNOWN'),
(6, 'VOIDED TRIP');

DROP TABLE IF EXISTS rates CASCADE;
CREATE TABLE rates(
    rate_code integer PRIMARY KEY,
    description text
);

INSERT INTO rates(rate_code, description) 
VALUES
(1, 'STANDARD RATE'),
(2, 'JFK'),
(3, 'NEWARK'),
(4, 'NASSAU OR WESTCHESTER'),
(5, 'NEGOTIATED FARE'),
(6, 'GROUP RIDE'),
(99, 'UNKOWN / ERROR');

/*
    FACT TABLE
*/
DROP TABLE IF EXISTS rides CASCADE;
CREATE TABLE rides (
    id serial PRIMARY KEY,
    load_datetime timestamp,
    pickup_datetime timestamp,
    dropoff_datetime timestamp,
    passenger_count integer,
    tip_amount real,
    total_amount real,
    /*
        Reference to other tables because for business purpose, 
        we should not use codes. Plus, using contraints to ensure data quality
        is a good practice.
    */
    payment_type integer
        REFERENCES payment_types(payment_type)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    rate_code integer
        references rates(rate_code)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    /*
        PostGIS datatype so that we can use it in a GIS 
    */
    pickup geometry(Point, 3857),
    dropoff geometry(Point, 3857)
);

/*
    Usually creating indices is a good idea to speed up queries. 
    However, indices may increase the size of the database considerably. 

    Indices are defining depending on the type of queries we want to apply
    frequently. Of course, these queries depend on business needs.

    Spacial indices are particularly importante. Have a look at:

    https://postgis.net/workshops/postgis-intro/indexing.html
*/
CREATE INDEX ON rides(pickup_datetime);
CREATE INDEX ON rides(passenger_count, pickup_datetime);

CREATE INDEX ON rides(pickup);
CREATE INDEX ON rides(dropoff);
