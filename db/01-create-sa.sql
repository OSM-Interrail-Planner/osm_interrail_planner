SET search_path TO sa;

/*
    The `rides` table records the rides data `as-is`
*/
DROP TABLE IF EXISTS rides;
CREATE TABLE rides (
    id serial PRIMARY KEY,
    pickup_datetime timestamp,
    dropoff_datetime timestamp,
    pickup_latitude real,
    pickup_longitude real,
    dropoff_latitude real,
    dropoff_longitude real,
    passenger_count integer,
    payment_type integer,
    rate_code integer,
    tip_amount real,
    total_amount real
);
