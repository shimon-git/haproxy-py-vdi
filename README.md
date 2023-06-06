# haproxy-py

This project combines HAProxy and CWM API to provide seamless integration and synchronization between them. The project utilizes a database called haproxy, which consists of three essential tables:

1. **API_KEYS**: This table stores the API keys required to execute commands in the CWM.
2. **SERVERS**: Contains information about the servers, including server_name, server_id, server_ip, server_sessions, backend, and idle_time.
3. **MAPS**: Stores user names that are mapped to the corresponding backend.

The haproxy-py script takes responsibility for synchronizing the haproxy database and configuration with the CWM. Additionally, it generates logs that can be found at the following path: `/var/log/haproxy-py.log`.

Now, let's proceed with the setup:

## Getting Started

To begin, clone the haproxy repository using the following command:

```shell
git clone https://github.com/shimon-git/haproxy-vdi.git
```

Make sure you have the required dependencies installed before running the script.
#Dependencies
The following dependencies are required to run haproxy-py:

  -  Python 3.x
  -  HAProxy
  -  CWM API
To install Python dependencies, use the following command:
```shell
pip install -r requirements.txt
```
