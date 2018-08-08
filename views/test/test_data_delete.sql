-- delete the test data
BEGIN;

DELETE FROM user WHERE 
username = 'doris' OR
username = 'John' OR
username = 'none'
;


COMMIT;