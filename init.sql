ALTER ROLE postgres PASSWORD 'Qq12345';
CREATE USER repl_user REPLICATION LOGIN PASSWORD 'Qq12345';

CREATE TABLE public.Email (
    id SERIAL PRIMARY KEY,
    mail VARCHAR(100) NOT NULL
);

CREATE TABLE public.Phone (
    id SERIAL PRIMARY KEY,
    number VARCHAR(50) NOT NULL
);

INSERT INTO Email (mail) VALUES ('test@test.test'), ('testone@tst.ru');
INSERT INTO Phone (number) VALUES ('+7(999) 123-11-00'), ('89777777777');
select pg_create_physical_replication_slot('replication_slot');