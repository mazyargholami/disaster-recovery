# Monitoring & Strategic Management

<p align="center"> <img  width=400 src="../assets/it-diasaster.png"> </p>

# Auto Strategy 

- ### 1. <a href="../nginx/">Nginx</a>
  - <a href="../nginx/default.conf">Registering Your Apps -> Add Healthy Check -> Add (fail_timeout) -> Auto Redirecting</a>

- ### 2. <a href="../django/">Apps</a>
  - Registerin Your Database -> Add Healthy Check -> Add (fail_timeout) -> Auto Renew Connection

- ### 3. <a href="../postgresql/">PostgreSQL DB </a> <a href="../monitoring/monitoring.sh">(Auto Failover)</a>
  - <a href="../postgresql#primary">DB1 (Main)</a>
    - Destroyed database
      ####
  - <a href="../postgresql#standby">DB2 (Standby)</a>
    - Sync to DB1 (Main) <- DB2 (Standby) -> Lost Connection (DB1 Main) -> Promote the Standby to Main
      ####
  - DB3 (Slave)
    - Sync to DB2 (Standby) <- DB3 (Slave) -> Lost Connection (DB2 Standby) -> Promote the Slave to Main
      ####

# <a href="../postgresql#create-a-full-backup">Manual Strategy</a>
 - ### 1. Take a base backup of your database
 - ### 2. Restore the Recovery Target Time
