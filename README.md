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

  -  **Python 3.7 or later**
  -  **HAProxy Built with Lua version**

#### To install Python dependencies, use the following command:

```shell
pip install -r requirements.txt
```

#### To check if your HAProxy installation supports Lua, you can use the following command in the terminal:

```shell
haproxy -vv | grep Lua
```

#### This command will display the version information for Lua if it is enabled in your HAProxy installation. If Lua support is enabled, the output will look like this:

```shell
Built with Lua version : Lua X.X.X
```

Please refer to the official documentation for HAProxy and CWM API installation instructions.

## Configuration
Before running the haproxy-py script, you need to configure the necessary settings.
Open the `haproxy/haproxy-py/haproxypy.yml` file and modify the following parameters according to your environment:


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


