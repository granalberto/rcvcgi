Para PostgreSQL:

createdb <database>

createlang plperl <database>

CREATE TABLE asesor (
id SERIAL PRIMARY KEY,
login VARCHAR(15) NOT NULL UNIQUE,
pass VARCHAR(20) NOT NULL,
nombre VARCHAR(20) NOT NULL,
apellido VARCHAR(20) NOT NULL,
ci VARCHAR(9) NOT NULL,
tlf CHAR(11) NOT NULL,
addr VARCHAR(100),
activo BOOLEAN NOT NULL DEFAULT TRUE);


CREATE TABLE vehiculo (
id SERIAL PRIMARY KEY,
placa VARCHAR(10) NOT NULL,
serial VARCHAR(25) NOT NULL,
marca VARCHAR(25) NOT NULL,
modelo VARCHAR(40) NOT NULL,
year CHAR(4) NOT NULL,
color VARCHAR(30) NOT NULL,
clase VARCHAR(20) NOT NULL,
tipo VARCHAR(20) NOT NULL,
uso VARCHAR(20) NOT NULL,
puestos VARCHAR(3) NOT NULL);

CREATE TABLE poliza (
id SERIAL PRIMARY KEY,
fname VARCHAR(30) NOT NULL,
lname VARCHAR(30) NOT NULL,
doc CHAR(1) NOT NULL,
ci VARCHAR(10) NOT NULL,
tlf CHAR(11) NOT NULL,
vehiculo_id INT NOT NULL REFERENCES vehiculo (id) ON DELETE RESTRICT,
asesor_id INT NOT NULL REFERENCES asesor (id) ON DELETE RESTRICT,
inicio TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
hash CHAR(16) NOT NULL UNIQUE,
prima NUMERIC(10,2) NOT NULL DEFAULT 200,
paid BOOLEAN NOT NULL DEFAULT FALSE,
control INT);

CREATE TABLE autokey (
seedname VARCHAR(10) NOT NULL PRIMARY KEY,
keyval INT NOT NULL);

INSERT INTO autokey VALUES('control', 1); -- Insertamos la semilla

CREATE OR REPLACE FUNCTION keygen() RETURNS trigger AS $$
spi_exec_query(q/BEGIN;/);
spi_exec_query(q/UPDATE autokey SET keyval = (keyval + 1) WHERE seedname = 'control';/);
my $val = spi_exec_query(q/SELECT keyval FROM autokey WHERE seedname = 'control';/);
$_TD->{new}{control} .= $val->{rows}[0]->{keyval} - 1;
spi_exec_query(q/COMMIT;/);
return 'MODIFY';
$$ LANGUAGE plperl;

CREATE TRIGGER keygen_trig 
BEFORE INSERT ON poliza 
FOR EACH ROW EXECUTE PROCEDURE keygen();



-- select poliza.placa, asesor.login, asesor.addr from poliza join asesor on poliza.asesor_id = asesor.id;

