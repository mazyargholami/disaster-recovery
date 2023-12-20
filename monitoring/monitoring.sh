#!/bin/bash

primary_host="localhost"
primary_port="5432"
standby_host="192.168.1.100"
standby_port="5432"
user="postgres"
password="mypassword"

# Check primary server status
pg_isready -h $primary_host -p $primary_port -U $user -W

if [[ $? -ne 0 ]]; then
  echo "Primary server failed! Promoting standby..."

  # Stop postgres on standby
  ssh $standby_host systemctl stop postgresql

  # Ensure replication isn't lagging
  standby_lag=$(psql -h $standby_host -p $standby_port -U $user -W -t -c "SELECT pg_last_replay_activity_time() - pg_current_time()")

  if [[ "$standby_lag" -lt '1 second' ]]; then
    echo "Standby is caught up. Promoting..."

    # Promote standby to primary
    ssh $standby_host systemctl start postgresql

    # Update DNS records or application configuration to point to new primary

    echo "Failover complete. New primary is $standby_host:$standby_port"
  else
    echo "Standby lag detected ($standby_lag). Failover aborted!"
  fi
else
  echo "Primary server is running."
fi
