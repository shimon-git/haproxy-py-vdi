CREATE DATABASE IF NOT EXISTS haproxy;
USE haproxy;


CREATE USER IF NOT EXISTS 'haproxy-py'@'localhost' IDENTIFIED BY 'Hh2023@!';
GRANT ALL PRIVILEGES ON haproxy.* TO 'haproxy-py'@'localhost';
FLUSH PRIVILEGES;


CREATE TABLE IF NOT EXISTS API_KEYS (
  api_id VARCHAR(50),
  api_secret VARCHAR(50)
);


CREATE TABLE IF NOT EXISTS SERVERS(
    server_name VARCHAR(50),
    server_id VARCHAR(100),
    server_ip VARCHAR(50),
    server_sessions VARCHAR(10),
    backend VARCHAR(50),
    server_status VARCHAR(50),
    idle_time VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS MAPS(
  rdp_cookie VARCHAR(50),
  backend VARCHAR(100)
)

INSERT INTO haproxy.API_KEYS (api_id, api_secret)
VALUES ('API-ID', 'API-SECRET');




