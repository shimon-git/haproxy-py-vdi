# haproxy-py description
this project combine haproxy and cwm API
this project used a DB named haproxy which contain 3 tables:
  1) API_KEYS - contain the api keys to execute commends in cwm
  2) SERVERS - contein the: server_name,server_id,server_ip,server_sessions,backend,idle_time
  3) MAPS - contain the user name that maps to the matching backend
 the haproxy-py is responsible to sync the haproxy DB, haproxy config with the cwm
 haproxy-py create logs in the follwing path: /var/log/haproxy-py.log
 
 lets start with the setup:
