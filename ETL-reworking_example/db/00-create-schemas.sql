CREATE EXTENSION postgis;

/*
    CREATE SCHEMAS
    It is a good practice, if space is not a problem, to divide the database 
    where the ETL process loads, to create a schema for the data `as-is` and 
    another schema where data is recorded to be used by the business users.
*/
CREATE SCHEMA sa; -- stagging area
CREATE SCHEMA pa; -- production area

