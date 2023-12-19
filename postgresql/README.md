# PostgreSQL Configurations 

    pg_basebackup -h primary_ip -U replication_user -D /path/to/standby/data -P --wal-method=stream
