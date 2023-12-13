# Disaster Recovery

## Nginx configurations
    http {
        upstream backend {
            server api1.example.com max_fails=3 fail_timeout=30s;
            server api2.example.com max_fails=3 fail_timeout=30s;
            # Add more servers as needed
        }
    
        server {
            listen 80;
            server_name example.com;
            return 301 https://$host$request_uri;
        }
    
        server {
            listen 443 ssl;
            server_name example.com;
    
            ssl_certificate /path/to/ssl/certificate.crt;
            ssl_certificate_key /path/to/ssl/private.key;
            ssl_protocols TLSv1.2 TLSv1.3;
            ssl_ciphers 'TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384';
    
            location / {
                proxy_pass http://backend;
                # Other proxy settings as needed
            }
    
            # Health check endpoint for api1.example.com
            location /health-api1 {
                access_log off;
                proxy_pass http://api1.example.com;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }
    
            # Health check endpoint for api2.example.com
            location /health-api2 {
                access_log off;
                proxy_pass http://api2.example.com;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }
        }
    }
## Postgresql
Synchronizing databases across multiple servers, often referred to as database replication, is a common practice to ensure data consistency and availability. In the context of PostgreSQL, there are several approaches to achieve database replication, and one popular method is to use streaming replication with a primary and one or more standby servers.

Here's a basic guide to set up streaming replication with two PostgreSQL servers:

#### 1. Configure the Primary Server:
Update the PostgreSQL configuration file (usually located at /etc/postgresql/{version}/main/postgresql.conf) on the primary server to enable streaming replication. Add or modify the following lines:

    listen_addresses = "*"
    wal_level = replica
    max_wal_senders = 3
    max_replication_slots = 3
Restart PostgreSQL for the changes to take effect.

#### 2. Create a Replication User:
Create a replication user on the primary server and grant necessary permissions:

    CREATE USER replication_user REPLICATION LOGIN CONNECTION LIMIT 5 ENCRYPTED PASSWORD 'your_password';
    
#### 3. Configure Primary Server for Replication:
Edit the pg_hba.conf file (usually located at /etc/postgresql/{version}/main/pg_hba.conf) to allow replication connections. Add the following line:

    host replication replication_user standby_ip/32 md5
Reload PostgreSQL for changes to take effect.

#### 4. Take a Base Backup on Standby:
On the standby server, take a base backup of the primary server. This is done using the pg_basebackup tool.

    pg_basebackup -h primary_ip -U replication_user -D /path/to/standby/data -P --wal-method=stream
Ensure that the data directory (/path/to/standby/data in this example) is empty before running the command.

#### 5. Configure Standby Server:
Create a recovery configuration file (recovery.conf) in the standby server's data directory with the following content:
/var/lib/postgresql/data/recovery.conf

    standby_mode = on
    primary_conninfo = 'host=primary_ip port=5432 user=replication_user password=your_password'
    restore_command = 'cp /path/to/archive/%f %p'
    trigger_file = '/path/to/standby/data/failover.trigger'
Adjust the values accordingly.

#### 6. Start Standby Server:
Start the standby server. PostgreSQL will continuously apply changes from the primary server's write-ahead log (WAL) files.

#### 7. Monitor Replication:
Use PostgreSQL's administrative functions to monitor replication 

status (pg_stat_replication, pg_stat_wal_receiver, etc.).

#### 8. Failover (Optional):
In case of a primary server failure, promote the standby server to become the new primary. This involves triggering the failover manually or using automated tools.




