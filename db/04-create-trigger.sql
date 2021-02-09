/*
    The purpose of the trigger is to insert into the pa.rides every time a new record is inserted
    in sa.rides. Plus, the longitude and latitude are converted into PostGIS datatypes.
*/
CREATE FUNCTION sa.insert_ride_in_pa()
RETURNS TRIGGER AS
$$
BEGIN
	INSERT INTO pa.rides(load_datetime, pickup_datetime, dropoff_datetime, 
			passenger_count, rate_code, tip_amount, payment_type, total_amount, pickup, dropoff) 
	VALUES (now(), new.pickup_datetime, new.dropoff_datetime, new.passenger_count, 
            new.rate_code, new.tip_amount, new.payment_type, new.total_amount, 
			ST_Transform(ST_SetSRID(ST_MakePoint(new.pickup_longitude, new.pickup_latitude), 4326), 3857),
			ST_Transform(ST_SetSRID(ST_MakePoint(new.dropoff_longitude, new.dropoff_latitude), 4326), 3857));
	RETURN new;
END;
$$
LANGUAGE 'plpgsql';

CREATE TRIGGER insert_rides_in_pa
AFTER INSERT ON sa.rides
FOR EACH ROW
EXECUTE PROCEDURE sa.insert_ride_in_pa();
