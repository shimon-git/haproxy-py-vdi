#pip install mysql-connector-python
import mysql.connector
from logger import Logger
class HaproxyDB():
    def __init__(self,host,user,password,database,port,tables):
            
        self.host= host
        self.user= user
        self.password= password
        self.database= database
        self.port = port
        self.api_table = tables['api_keys_table']
        self.servers_table = tables['servers_table']
        self.maps_table = tables['map_table']
        self.logger = Logger()
        self.log = self.logger.setup_logger()

    def start_connection(self):
        try:
            self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    port=self.port
                    )
            self.log.info('Connection with the haproxy database established successfully!')
            self.cursor = self.connection.cursor()
        except mysql.connector.Error as error:
            if error.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                self.log.critical(f'{self.logger.function_name()} - Invalid credentials for haproxy database. Please check your username and password.')
            elif error.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.log.critical(f'{self.logger.function_name()} - The specified database does not exist. (database: {self.database})')
            elif error.errno == mysql.connector.errorcode.CR_CONN_HOST_ERROR:
                self.log.critical(f'{self.logger.function_name()} - Connection refused. Please check the host address alternatively check the mysql service is running!.')
            else:
                self.log.critical(f'{self.logger.function_name()} An error occurred: {error}')

    def close_connection(self):
        self.cursor.close()
        self.connection.close()


    def get_api_keys(self):
        self.start_connection()
        self.cursor.execute("SELECT * FROM %s;"%self.api_table)
        rows = self.cursor.fetchall()
        if len(rows) != 0:
            for row in rows:
                for column_name, value in zip(self.cursor.column_names,row):
                    if value is None:
                        self.log.error(f'{self.logger.function_name()} - The retrieval of API keys from the database failed due to an empty response received from the database. (column name: {column_name})')
        else: self.log.error(f'{self.logger.function_name()} - Unknown error please check the database!')
        self.close_connection()
        return rows[0]
        

    def get_server(self,identity,identity_value,value='*'):
        if (identity,identity_value) == (None,None):
            self.log.error(f'{self.logger.function_name()} - Empty parameters were received: parameter names (identify, identify_value).')
        self.start_connection()
        query = f"select {value} FROM {self.servers_table} where {identity} = '{identity_value}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.close_connection()
        self.log.info('Successfully retrieved server information from the database.')
        return None if len(rows) == 0 else 'duplicated serves' if len(rows) > 1 else rows[0]


    def update_server_list(self,new_server,idle_time):
        if self.get_server('server_id',new_server['server_id']) == 'duplicated serves' or type(self.get_server('server_id',new_server['server_id'])) == tuple:
            self.log.info('Cannot add a new server to the database. Reason: The server already exists.')
            return
        query = f"INSERT into {self.servers_table} (server_name, server_id, server_ip, server_sessions, backend, server_status,idle_time) VALUES (%s,%s,%s,%s,%s,%s,%s);"
        self.start_connection()
        self.cursor.execute(query, (new_server['server_name'], new_server['server_id'], new_server['server_ip'], new_server['server_sessions'],new_server['backend'],new_server['server_status'],idle_time))
        self.connection.commit()
        affected_rows = self.cursor.rowcount
        self.close_connection()
        if  affected_rows > 0:  self.log.info('Successfully added a new server to the database.')
        else: self.log.warning(f"{self.logger.function_name()} - Failed to add a new server to the server list. (server: {new_server['server_name']})")
        
    
    def get_server_list(self):
        query = 'SELECT * FROM %s;'%self.servers_table
        self.start_connection()
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.close_connection()
        self.log.info('Successfully retrieved the server list information from the database.')
        return rows


    def delete_server(self, server_id):
        if self.get_server('server_id',server_id) == None:
            self.log.info('Cannot delete the server from the database. The specified server does not exist in the database.')
            return
        query = f"DELETE FROM {self.servers_table} WHERE server_id = '%s';"%server_id
        self.start_connection()
        self.cursor.execute(query)
        self.connection.commit()
        affected_rows = self.cursor.rowcount
        self.connection.commit()
        self.close_connection()
        if  affected_rows > 0:  self.log.info(f'Successfully deleted the server from the database. (server id: {server_id})')
        else: self.log.warning(f"{self.logger.function_name()} - Failed to delete the server from the database. (server id: {server_id})")


    def update_server_data(self,identity,identity_value,column,data):
        try:
            if self.get_server(identity,identity_value,column)[0] == data:
                self.log.info(f'Cannot update the server data in the database. The server data is already up to date and no changes were made.(identity: {identity},identity_value: {identity_value})')
                return
        except TypeError:
            self.log.exception(f'{self.logger.function_name()} - Failed to update the server data. The server is not found in the database.')
            return
        query = f"UPDATE {self.servers_table} SET {column} = %s WHERE {identity} = %s;"
        self.start_connection()
        self.cursor.execute(query, (data,identity_value))
        self.connection.commit()
        affected_rows = self.cursor.rowcount
        self.close_connection()
        if  affected_rows > 0: self.log.info(f'Server data has been successfully updated. (identity: {identity},identity_value: {identity_value})')
        else: self.log.error(f'{self.logger.function_name()} - Failed to update server data. (identity: {identity},identity_value: {identity_value})')
        
    
    def get_backends(self):
        query = f"SELECT backend FROM {self.servers_table};"
        self.start_connection()
        self.cursor.execute(query)
        rows = self.cursor.fetchall() 
        self.close_connection()
        self.log.info('Successfully retrieved backend information from the database.')
        return [backend[0] for backend in rows if backend[0] not in (None, '')]
       

    def get_maps(self):
        query = f"SELECT * FROM {self.maps_table};"
        self.start_connection()
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.log.info('Successfully retrieved maps information from the database.')
        self.close_connection()
        return rows
    
    def delete_map(self,map_key):
        query = f"DELETE FROM {self.maps_table} WHERE rdp_cookie = '%s';"%map_key
        self.start_connection()
        self.cursor.execute(query)
        self.connection.commit()
        self.close_connection()
        self.log.info(f'Successfully deleted map entry from the database. (map_key: {map_key})')

    def add_map(self,map_key,map_value):
        query = f"INSERT INTO {self.maps_table} (rdp_cookie, backend) VALUES (%s,%s);"
        self.start_connection()
        self.cursor.execute(query, (map_key,map_value))
        self.connection.commit()
        self.close_connection()
        self.log.info(f'Successfully added map entry to the database. (map_key: {map_key})')
    
    def update_map(self,map_key,map_value):
        query = f"UPDATE {self.maps_table} SET backend = %s WHERE rdp_cookie = %s;"
        self.start_connection()
        self.cursor.execute(query, (map_value,map_key))
        self.connection.commit()
        self.close_connection()
        self.log.info(f'Successfully updated map entry in the database. (map_key: {map_key})')
