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
        self.critical_logs = {
            "invalid_credentials": "Invalid credentials for haproxy database. Please check your username and password.",
            "db_not_exist": "The specified database does not exist. (database: {database}).",
            "connection_refused": "Connection refused. Please check the host address alternatively check the mysql service is running!.",
            "general_error": "An error occurred: {err}"
        }
        self.info_logs = {
            "db_connection": "Connection with the haproxy database established successfully!",
            "server_info": "Successfully retrieved server information from the database.",
            "new_server_added": "Successfully added a new server named {server_name} to the database.",
            "server_list_info": "Successfully retrieved the server list information from the database.",
            "server_deletion": "Successfully deleted the server from the database. (server id: {srv_id})",
            "server_update": "Server data has been successfully updated. (identity: {srv_identity},identity_value: {srv_identity_value})",
            "backend_info": "Successfully retrieved backend information from the database.",
            "maps_info": "Successfully retrieved maps information from the database.",
            "map_deletion": "Successfully deleted map entry from the database. (map_key: {map})",
            "map_added": "Successfully added map entry to the database. (map_key: {map})",
            "map_update": "Successfully updated map entry in the database. (map_key: {map})"
        }
        self.error_logs = {
            "api_key_retrieval": "The retrieval of API keys from the database failed due to an empty response received from the database. (column name: {column})",
            "unknown_error": "Unknown error please check the database!",
            "empty_params": "Empty parameters were received: parameter names ({parameters}).",
            "server_update": "Failed to update server data. (identity: {srv_identity},identity_value: {srv_identity_value})"
        }
        self.warning_logs = {
            "delete_noexist_server": "Cannot delete the server '{srv_id}' from the database. The specified server does not exist in the database.",
            "failed_deletion": "Failed to delete the server from the database. (server id: {srv_id})",
            "server_already_exist": "Cannot add a new server to the database. Reason: The server {server_name} already exists.",
            "server_already_up_to_date": "Cannot update the server data in the database. The server data is already up to date and no changes were made.(identity: {srv_identity},identity_value: {srv_identity_value})",
            "update_noexist_server": "Failed to update the server data. The server is not found in the database - (identity: {srv_identity},identity_value: {srv_identity_value})."
        }
        self.queries = {
            "get_all_from": "SELECT * FROM {table};",
            "select_item": "SELECT {item} FROM {table} WHERE {item_property} = '{item_value}';",
            "get_item": "SELECT {item} FROM {table};",
            "insert_into": "INSERT into {table} ({props}) VALUES ({place_holders});",
            "delete_item": "DELETE FROM {table} WHERE {item_property} = '{item_value}';",
            "update_item": "UPDATE {table} SET {item_property} = %s WHERE {item_value} = %s;"
        }

    def start_connection(self):
        try:
            self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    port=self.port
                    )
            self.log.info(self.logger.log_reformat(self.info_logs["db_connection"]))
            self.cursor = self.connection.cursor()
        except mysql.connector.Error as error:
            if error.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                self.log.critical(self.logger.log_reformat(self.critical_logs["invalid_credentials"]))
            elif error.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.log.critical(self.logger.log_reformat(self.critical_logs["db_not_exist"].format(database=self.database)))
            elif error.errno == mysql.connector.errorcode.CR_CONN_HOST_ERROR:
                self.log.critical(self.logger.log_reformat(self.critical_logs["connection_refused"]))
            else:
                self.log.critical(self.logger.log_reformat(self.critical_logs["connection_refused"].format(err=error)))

    def query(self,query,params=None,commit=False,get_affected_rows=False):
        self.start_connection()
        self.cursor.execute(query, params) if params else self.cursor.execute(query)
        self.connection.commit() if commit else None
        affected_rows = self.cursor.rowcount
        rows = self.cursor.fetchall()
        self.close_connection()
        return affected_rows if get_affected_rows else rows

    def close_connection(self):
        self.cursor.close()
        self.connection.close()


    def get_api_keys(self):
        query = self.queries["get_all_from"].format(table=self.api_table)
        rows = self.query(query=query)
        if len(rows) != 0:
            for row in rows:
                for column_name, value in zip(self.cursor.column_names,row):
                    if value is None:
                        self.log.error(self.logger.log_reformat(self.error_logs["api_key_retrieval"].format(column=column_name)))
        else: self.log.error(self.log.error(self.logger.log_reformat(self.error_logs["unknown_error"])))
        return rows[0]
        

    def get_server(self,identity,identity_value,value='*'):
        if (identity,identity_value) == (None,None):
            self.log.error(self.log.error(self.logger.log_reformat(self.error_logs["empty_params"].format(parameters="identify, identify_value"))))
        query = self.queries["select_item"].format(item=value,table=self.servers_table,item_property=identity,item_value=identity_value)
        rows = self.query(query=query)
        self.log.info(self.logger.log_reformat(self.info_logs["server_info"]))
        return None if len(rows) == 0 else 'duplicated serves' if len(rows) > 1 else rows[0]


    def update_server_list(self,new_server,idle_time):
        if self.get_server('server_id',new_server['server_id']) == 'duplicated serves' or type(self.get_server('server_id',new_server['server_id'])) == tuple:
            self.log.warning(self.logger.log_reformat(self.warning_logs["server_already_exist"].format(server_name=new_server['server_name'])))
            return
        query = self.queries["insert_into"].format(
            table=self.servers_table,
            props="server_name, server_id, server_ip, server_sessions, backend, server_status,idle_time",
            place_holders="%s,%s,%s,%s,%s,%s,%s"
        )
        params = (
            new_server['server_name'], 
            new_server['server_id'], 
            new_server['server_ip'], 
            new_server['server_sessions'],
            new_server['backend'],
            new_server['server_status'],
            idle_time
        )
        affected_rows = self.query(query=query, get_affected_rows=True, params=params)
        self.log.info(self.logger.log_reformat(self.info_logs["new_server_added"].format(server_name=new_server['server_name']))) if  affected_rows > 0 else self.log.warning(f"{self.logger.function_name()} - Failed to add a new server to the server list. (server: {new_server['server_name']})")
        
    
    def get_server_list(self):
        query = self.queries["get_all_from"].format(table=self.servers_table)
        rows = self.query(query)
        self.log.info(self.logger.log_reformat(self.info_logs["server_list_info"]))
        return rows


    def delete_server(self, server_id):
        if self.get_server('server_id',server_id) == None:
            self.log.warning(self.logger.log_reformat(self.warning_logs["delete_noexist_server"].format(srv_id=server_id)))
            return
        query = self.queries["delete_item"].format(
            table=self.servers_table,
            item_property="server_id",
            item_value=server_id
        )
        affected_rows = self.query(query=query,commit=True,get_affected_rows=True)
        if  affected_rows > 0:  self.log.info(self.logger.log_reformat(self.warning_logs["failed_deletion"].format(srv_id=server_id)))
        else: self.log.warning(self.logger.log_reformat(self.warning_logs["failed_deletion"].format(srv_id=server_id)))

    # pay attention
    def update_server_data(self,identity,identity_value,column,data):
        try:
            if self.get_server(identity,identity_value,column)[0] == data:
                self.log.warning(self.logger.log_reformat(self.warning_logs["server_already_up_to_date"].format(srv_identity=identity, srv_identity_value=identity_value)))
                return
        except TypeError:
            self.log.exception(self.logger.log_reformat(self.warning_logs["update_noexist_server"].format(srv_identity=identity, srv_identity_value=identity_value)))
            return
        
        query = self.queries["update_item"].format(
            table=self.servers_table,
            item_property=column,
            item_value=identity
        )
        affected_rows = self.query(query=query,get_affected_rows=True)
        if  affected_rows > 0: self.log.info(self.logger.log_reformat(self.info_logs["server_update"].format(srv_identity=identity, srv_identity_value=identity_value)))
        else: self.log.error(self.logger.log_reformat(self.error_logs["server_update"].format(srv_identity=identity, srv_identity_value=identity_value)))
        
    
    def get_backends(self):
        query = self.queries["update_item"].format(
            item="backend",
            table=self.servers_table
        )
        rows = self.query(query)
        self.log.info(self.logger.log_reformat(self.info_logs["backend_info"]))
        return [backend[0] for backend in rows if backend[0] not in (None, '')]


    def get_maps(self):
        query = self.queries["get_all_from"].format(table=self.maps_table)
        rows = self.query(query)
        self.log.info(self.logger.log_reformat(self.info_logs["maps_info"]))
        return rows
    
    def delete_map(self,map_key):
        query = self.queries["delete_item"].format(
            table=self.maps_table,
            item_property="rdp_cookie",
            item_value=map_key
        )
        self.query(query=query,commit=True)
        self.log.info(self.logger.log_reformat(self.info_logs["map_deletion"].format(map=map_key)))
    
    def add_map(self,map_key,map_value):
        query = self.queries["insert_into"].format(
            table=self.maps_table,
            props="rdp_cookie, backend",
            place_holders="%s,%s"
        )
        params = (map_key,map_value)
        self.query(query=query,params=params,commit=True)
        self.log.info(self.logger.log_reformat(self.info_logs["map_added"].format(map=map_key)))
    
    def update_map(self,map_key,map_value):
        query = self.queries["update_item"].format(
            table=self.maps_table,
            item_property="backend",
            item_value="rdp_cookie"
        )        
        params = (map_value,map_key)
        self.query(query=query,params=params,commit=True)
        self.log.info(self.logger.log_reformat(self.info_logs["map_update"].format(map=map_key)))
