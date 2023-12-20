# PostgreSQL Archiving and Point-in-Time Recovery (PITR)

<p align="center" ><img width=800 src="../assets/fig-10-02.png"> </p>

## Enable Archiving
- In the postgresql.conf file, set the archive_mode configuration parameter to on. This will enable archiving.
  
## Configure Archive Command
- In the postgresql.conf file, set the archive_command configuration parameter to a command that will copy the WAL files to a safe location. For example, you can use the following command:

		# directory structure, I used in this tutorial
		/u01    - PostgreSQL Data Directory Mount
		/u02    - Wal Archives Mount
		/backup - Backups Mount
		
		# data dir
		/u01/h1_dev_db/data
		
		# create directory for wal_archives
		mkdir -p /u02/hl_dev_db/wal_archive
		chown postgres:postgres -R /u02/hl_dev_db/wal_archive
		
		vim /u01/h1_dev_db/data/postgresql.conf
		...
		archive_mode = on
		archive_command = 'cp %p /u02/hl_dev_db/wal_archive/%f'
		...
- This command will copy the WAL file to /u02/hl_dev_db/wal_archive/ directory.

## Create a Full Backup
- Take a base backup of your database using the following command:

  
		export DATESTAMP=$(date +%Y-%m-%d)
		
		mkdir -p /backup/hl_dev_db_full_bkp_$DATESTAMP
		
		chown postgres:postgres -R /backup 
		
		# Create full backup using pg_basebackup
		pg_basebackup -D /backup/hl_dev_db_full_bkp_2023-03-09 -Ft -z -P -Xs
		
		# -F format = TAR ( t )
		# -z compression = gzip
		# -P Progress
		# -Xs wal method = stream

## CASE1: Restore the Recovery Target Time
<p align="center" ><img width=800 src="../assets/fig-10-05.png"> </p>

	# create new pg_data dir
	mkdir -p /u01/hl_dev_db_recovery/data
	chown postgres:postgres -R /u01/hl_dev_db_recovery/data
	chmod 0750 -R /u01/hl_dev_db_recovery/data
	
	# Untar the backup
	tar -xvf /backup/hl_dev_db_full_bkp_2023-03-09/base.tar.gz -C /u01/hl_dev_db_recovery/data/
	tar -xvf /backup/hl_dev_db_full_bkp_2023-03-09/pg_wal.tar.gz -C /u01/hl_dev_db_recovery/data/pg_wal/
	
	# For Instance, you want to restore the database for Timestamp 15:45
	# at 15:45 : we only have employees table in postgres db
	
	# add the recovery settings to postgresql
	# Adding recovery settings 
	vim /u01/hl_dev_db_recovery/data/postgresql.conf 
	---
	restore_command = 'cp /u02/hl_dev_db/wal_archive/%f "%p"'
	recovery_target_time = '2023-03-08 15:45:00'
 	# or
  	recovery_target_time = "2023-03-08 15:45:00 GMT"
	---
	
	# start the database 
	pg_ctl start -D /u01/hl_dev_db_recovery/data -w -t 300 -l logfile
	
	# check logs for recovery process
	tail -200f /u01/hl_dev_db_recovery/data/log/postgresql-Thu.log

## CASE2 : Restore to Recovery Target
<p align="center" ><img width=800 src="../assets/fig-10-04.png"> </p>

	# stop database
	pg_ctl stop -D /u01/hl_dev_db_recovery/data
	
	# change time in postgresql.conf
	vim /u01/hl_dev_db_recovery/data/postgresql.conf 
	---
	recovery_target = 'immediate'
	---
	
	# start the database 
	pg_ctl start -D /u01/hl_dev_db_recovery/data -w -t 300 -l logfile
	
	# check logs for recovery process
	tail -200f /u01/hl_dev_db_recovery/data/log/postgresql-Thu.log

# PostgreSQL Disaster Configurations 

<p align="center" ><img width=400 src="../assets/Multimaster-1.png"> </p>

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
- #### vim /etc/letsencrypt/renewal-hooks/deploy/postgresql.deploy
		#!/bin/bash
		umask 0177
		DOMAIN=psql.example.com
		DATA_DIR=/var/lib/postgresql/12/main
		cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $DATA_DIR/server.crt
		cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $DATA_DIR/server.key
		chown postgres:postgres $DATA_DIR/server.crt $DATA_DIR/server.key

- chmod +x /etc/letsencrypt/renewal-hooks/deploy/postgresql.deploy

- #### vim postgresql.conf
		ssl = on
		ssl_cert_file = 'server.crt'
		ssl_key_file = 'server.key'
		ssl_prefer_server_ciphers = on

- #### vim pg_hba.conf
		# Allow replication connections from localhost , by a user with the
		# replication privilege
		hostssl		all	all	0.0.0.0/0	md5
		host		all	all	0.0.0.0/0	md5

- ls /var/lib/postgresql/12/main/server.*

- /usr/lib/postgresql/16/bin/pg_ctl -D /home/stark/Projects/lab/database/replica_db restart

## Testing SSL Connection
	psql -d "dbname=postgres sslmode=require" -h psql.example.com -U postgres

## Extra Info
	psql -d postgresql://postgres:password@localhost:5432/dbname -c "create database sample1 --or any command"

	pg_lsclusters







    
