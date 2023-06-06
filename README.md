# haproxy-py

This project combines HAProxy and CWM API to provide seamless integration and synchronization between them. The project utilizes a database called haproxy, which consists of three essential tables:

1. **API_KEYS**: This table stores the API keys required to execute commands in the CWM.
2. **SERVERS**: Contains information about the servers, including server_name, server_id, server_ip, server_sessions, backend, and idle_time.
3. **MAPS**: Stores user names that are mapped to the corresponding backend.

The haproxy-py script takes responsibility for synchronizing the haproxy database and configuration with the CWM. Additionally, it generates logs that can be found at the following path: `/var/log/haproxy-py.log`.

Now, let's proceed with the setup:

## Getting Started

#### To begin, clone the haproxy repository using the following command:

```shell
git clone https://github.com/shimon-git/haproxy-vdi.git
```

Make sure you have the required dependencies installed before running the script.
## Dependencies
The following dependencies are required to run haproxy-py:

  -  Python 3.x
  -  HAProxy
  -  CWM API

#### To install Python dependencies, use the following command:

```shell
pip install -r requirements.txt
```

Please refer to the official documentation for HAProxy and CWM API installation instructions.

## Configuration
Before running the haproxy-py script, you need to configure the necessary settings.
Open the `haproxy/haproxy-py/haproxypy.yml` file and modify the following parameters according to your environment:


```yaml
# dataplane api configurations
dataplaneapi:
  user: admin
  password: adminpwd
  host: 127.0.0.1
  port: 5555
  
  # database conf
DB:
  host: 127.0.0.1
  user: haproxy-py
  password: Hh2023@!
  database: haproxy
  port: 3306
  tables:
    api_keys_table: API_KEYS
    servers_table: SERVERS
    map_table: MAPS
    
# backends conf
haproxy_backend_config:
  mode: tcp
  server_port: 3389
  tcp_delay_inspection: 5
  lua_action: turn_on_server
  server_timeout: 50000
  connect_timeout: 50

# servers conf
global_servers:
  name: training.it
  network: 172.16.0.0
  # put the USERNAME keyword where the username is on the global server names --> training.it.shimon is: training.it.USERNAME
  username: training.it.USERNAME
  
  # idle time conf
  idle_time:
  # server_on/suspended/off will represent the status of the servers that are in state of on/suspended/off in the haproxy DB
  server_on: RUNNING
  server_suspended: SUSPENDED
  server_off: OFF
  # timeout represent the timeout of idle time in minutes before it's will be suspended
  timeout: 5
  # interval represent the interval time for checking the state  of the servers
  interval: 5
  
# The sleep_checker represents the time to wait before checking if the CWM commands were completed successfully.
  sleep_checker: 12
```

  -  haproxy_db_path: Specify the path to your haproxy database file.
  -  cwm_api_url: Provide the URL of your CWM API endpoint.
  -  cwm_api_key: Enter your API key for CWM authentication.

## Usage

To execute the haproxy-py script, run the following command:

```shell
python haproxy-py.py
```

# Logs

The haproxy-py script generates logs during its operation. You can find the log file at the following location:

`
/var/log/haproxy-py.log
`

# Contributing

We welcome contributions to the haproxy-py project. If you find any issues or have suggestions for improvements, please submit a pull request or open an issue on the project's GitHub repository.

# License

This project is licensed under the MIT License. Feel free to use, modify, and distribute it as per the license terms.


We hope you find haproxy-py useful and enjoy using it in your environment. Should you have any questions or need assistance, please don't hesitate to contact us.


