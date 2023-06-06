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

### Donwnload Python3 and pip:

```shell
sudo apt update
sudo apt install python3-pip
sudo apt install python3-pip
```

### Donwnload apache2,mysql,haproxy:

```shell
sudo apt install apache2
sudo apt install mysql-server
sudo systemctl enable apache2
sudo systemctl enable mysql
```

### Configure and secure mysql:

```shell
mysql -u root
use mysql;
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'new_password';
FLUSH PRIVILEGES;
exit
```

#### Run the mysql_secure_installation script:

```shell
sudo mysql_secure_installation
```

### Initialize the haproxy Database:

Edit the `init_db.sql` file:

```shell
cd haproxy-py-vdi
vi init_db.sql
```

In line 32 replace this: `('API-ID', 'API-SECRET')` with your API-ID and your API-SECRET.

connect to mysql and initialize the haporxy database:

```shell
mysql -u root -p
source PATH/To/haproxy-vdi/init_db.sql
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

#### If Lua support is enabled, the output will look like this:

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


