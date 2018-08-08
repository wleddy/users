-- Sample data for testing Shotglass
BEGIN;

INSERT INTO user (first_name,last_name,email,username,active) VALUES ('Doris','Goodman','doris@example.com','doris',1);
INSERT INTO user (first_name,last_name,email,username,active) VALUES ('John','Goodman','John@example.com','John',1);
INSERT INTO user (first_name,last_name,email,username,active) VALUES ('No one','in particular','noone@example.com','none',0);

-- Create user_roles
INSERT INTO user_role (user_id,role_id) VALUES (
    (select id from user where username = 'doris'),
    (select id from role where name = 'admin')
);
INSERT INTO user_role (user_id,role_id) VALUES (
    (select id from user where username = 'John'),
    (select id from role where name = 'user')
);

COMMIT;
