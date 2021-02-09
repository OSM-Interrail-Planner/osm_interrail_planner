SET search_path TO pa;

------------------------------------------------------------------------------------------------
-- EXAMPLE OF USE
-- SELECT * FROM generate_time_buckets('5 min');
DROP FUNCTION IF EXISTS generate_time_buckets;
CREATE OR REPLACE FUNCTION generate_time_buckets(dt interval) 
RETURNS TABLE (t0 time, t1 time) AS
$$
BEGIN
	RETURN QUERY
	SELECT dd::time AS t0, (dd + dt)::time AS t1
	-- dummy date
	FROM generate_series('2000-01-01 00:00:00'::timestamp, 
					 '2000-01-01 23:59:59'::timestamp, dt::interval) dd;
END;
$$
LANGUAGE plpgsql;

------------------------------------------------------------------------------------------------
-- EXAMPLE OF USE
-- SELECT * FROM generate_timestamp_buckets('2021-01-01', '2021-02-28', '5 min');
DROP FUNCTION IF EXISTS generate_timestamp_buckets;
CREATE OR REPLACE FUNCTION generate_timestamp_buckets(ts0 timestamp, ts1 timestamp, dt interval) 
RETURNS TABLE (t0 timestamp, t1 timestamp) AS
$$
BEGIN
	RETURN QUERY
	SELECT dd::timestamp AS t0, (dd + dt)::timestamp AS t1
	FROM generate_series(ts0, ts1, dt::interval) dd;
END;
$$
LANGUAGE plpgsql;
