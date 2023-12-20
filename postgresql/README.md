# PostgreSQL Configurations 

## Primary
 	locate initdb
	mkdir primary_db # if you create directory you should check the permission we suggest to don't create directory to automaticly create it by initdb
	cd primary_db
	mkdir tmp
	/usr/lib/postgresql/16/bin/initdb -D /home/stark/Projects/lab/database/primary_db
- #### vim /home/stark/Projects/lab/database/primary_db/postgresql.conf
		listen_addresses = '*'
		port = 5433
		unix_socket_directories = '/home/stark/Projects/lab/database/primary_db/tmp/'
		max_wal_senders = 10
		wal_level = replica
		max_replication_slots = 10
		# synchronous_commit = on
		# synchronous_standby_names = '*'

	- sudo chmod +x /var/run/postgresql # if you don't wanna use initdb
	- /usr/lib/postgresql/16/bin/pg_ctl -D /home/stark/Projects/lab/database/primary_db -l logfile start
	- /usr/lib/postgresql/16/bin/pg_ctl -D /home/stark/Projects/lab/database/primary_db start
	- /usr/lib/postgresql/16/bin/pg_ctl -D /home/stark/Projects/lab/database/primary_db stop

- #### psql --port=5433 postgres --host=/home/stark/Projects/lab/database/primary_db/tmp
  
		CREATE USER repuser REPLICATION LOGIN CONNECTION LIMIT 5 ENCRYPTED PASSWORD 'your_password';
		SELECT pg_create_physical_replication_slot('hot_standby_1');
		\q

- #### vim /home/stark/Projects/lab/database/primary_db/pg_hba.conf
		# IPv4 local connections:
		host	all	repuser		<standby_ip>/32	trust

- /usr/lib/postgresql/16/bin/pg_ctl -D /home/stark/Projects/lab/database/primary_db restart



## Standby 
	mkdir replica_db # if you create directory you should check the permission we suggest to don't create directory to automaticly create it by initdb
	pg_basebackup -h <primary_ip> -U repuser --checkpoint=fast \
		-D /home/stark/Projects/lab/database/replica_db -R --slot=some_name -C --port=5433
#### or
	pg_basebackup -h primary_ip -U repuser -D /home/stark/Projects/lab/database/replica_db -P --wal-method=stream

- cd replica_db
- cat postgresql.auto.conf
- mkdir tmp
- #### vim postgresql.conf
		listen_addresses = '*'
		port = 5434
		unix_socket_directories = '/home/stark/Projects/lab/database/replica_db/tmp/'
		hot_standby_feedback = on
		primary_slot_name = 'hot_standby_1'
		hot_standby = on
		archive_mode = on
		primary_conninfo = 'host=127.0.0.1 port=5433 user=repuser password=your_password'
		recovery_target_timeline = 'latest'
		archive_command = 'cd'

- /usr/lib/postgresql/16/bin/pg_ctl -D /home/stark/Projects/lab/database/replica_db start

## Primary
- psql --port=5433 postgres --host=/home/stark/Projects/lab/database/primary_db/tmp
  ####
		\x
		select * from pg_stat_replication;

## Standby
- psql postgres --port=5434 --host=/home/stark/Projects/lab/database/replica_db/tmp
  ####
		\x
		select * from pg_stat_wal_receiver;

## Primary
- psql --port=5433 postgres --host=/home/stark/Projects/lab/database/primary_db/tmp
  ####
		\x
		create table tbl(id int);
		insert into tbl values(1);
		insert into tbl values(2);
		\x

## Standby
- psql postgres --port=5434 --host=/home/stark/Projects/lab/database/replica_db/tmp
  ####
		select * from tbl;

## Manual make standby to primary
- /usr/lib/postgresql/16/bin/pg_ctl promote -D /home/stark/Projects/lab/database/replica_db

## SSL
vim /etc/letsencrypt/renewal-hooks/deploy/postgresql.deploy
	#!/bin/bash
	umask 0177
	DOMAIN=psql.example.com
	DATA_DIR=/var/lib/postgresql/12/main
	cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $DATA_DIR/server.crt
	cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $DATA_DIR/server.key
	chown postgres:postgres $DATA_DIR/server.crt $DATA_DIR/server.key

chmod +x /etc/letsencrypt/renewal-hooks/deploy/postgresql.deploy

vim postgresql.conf
	ssl = on
	ssl_cert_file = 'server.crt'
	ssl_key_file = 'server.key'
	ssl_prefer_server_ciphers = on

vim pg_hba.conf
	# Allow replication connections from localhost , by a user with the
	# replication privilege
	hostssl		all	all	0.0.0.0/0	md5
	host		all	all	0.0.0.0/0	md5

ls /var/lib/postgresql/12/main/server.*

/usr/lib/postgresql/16/bin/pg_ctl -D /home/stark/Projects/lab/database/replica_db restart

## Testing SSL Connection
psql -d "dbname=postgres sslmode=require" -h psql.example.com -U postgres

## Extra Info
psql -d postgresql://postgres:password@localhost:5432/dbname 
-c "create database sample1 --or any command"

pg_lsclusters







    
