#!/usr/bin/python3
import subprocess
import json
from sql import HaproxyDB
from time import sleep
from haproxy_api import HaproxyApi
import yaml
from logger import Logger
class servers():
    def __init__(self):
        self.logger = Logger()
        self.log = self.logger.setup_logger()
        self.config_file_name = r'/etc/haproxy/haproxy-py/haproxypy.yml'
        self.suspend_servers_list = []
        self.load_configuration_file()
    
    def load_configuration_file(self):
        with open(self.config_file_name, 'r') as config_file:
            configuration = yaml.safe_load(config_file)
        try:
            self.haDB = HaproxyDB(
                configuration['DB']['host'],
                configuration['DB']['user'],
                configuration['DB']['password'],
                configuration['DB']['database'],
                int(configuration['DB']['port']),
                configuration['DB']['tables'],
            )
            self.ha_api = HaproxyApi(
                configuration['dataplaneapi']['user'],
                configuration['dataplaneapi']['password'],
                configuration['dataplaneapi']['host'],
                configuration['dataplaneapi']['port'],
                configuration['haproxy_backend_config']
            )
            self.idle_time = {
                'on': configuration['idle_time']['server_on'],
                'off': configuration['idle_time']['server_off'],
                'suspended': configuration['idle_time']['server_suspended'],
                'timeout': int(configuration['idle_time']['timeout']),
                'interval' : int(configuration['idle_time']['timeout']),
            }
            self.global_servers = {
                'name': configuration['global_servers']['name'],
                'username': configuration['global_servers']['username'].lower(),
                'network': '.'.join(configuration['global_servers']['network'].split('.')[:-1]),
            }
            self.sleep_checker = int(configuration['sleep_checker'])
        except KeyError:
            self.log.exception(f'{self.logger.function_name()} KeyError, - faild to load config file!')
            exit()
    
    
    def cwm_command(self,command,server_id=None,server_name=None):
        api_keys = self.haDB.get_api_keys() #(API_ID, API_SECRET)
        cmd = None
        api_auth_error = 'your ip address is not allowed.'
        if command == 'servers list':
           cmd = f"cloudcli server list --api-clientid {api_keys[0]} --api-secret {api_keys[1]} --format json"
        elif command == 'server info':
            cmd = f"cloudcli server info --id {server_id} --api-clientid {api_keys[0]} --api-secret {api_keys[1]} --format json"
        elif command == 'server resume':
             cmd = f"cloudcli server resume --id {server_id} --api-clientid {api_keys[0]} --api-secret {api_keys[1]} --format json"
        elif command == 'server suspend':
            cmd = f"cloudcli server suspend --id {server_id} --api-clientid {api_keys[0]} --api-secret {api_keys[1]} --format json"
        elif command == 'server poweron':
            cmd = f"cloudcli server poweron --id {server_id} --api-clientid {api_keys[0]} --api-secret {api_keys[1]} --format json"
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        if output:            
            if 'errors' in str(output):
                if output.get('errors') and len(output['errors']) > 0 and output['errors'][0].get('info') == api_auth_error:
                    self.log.critical(f'There is an error with the API authentication. (command = {command})')
                else:
                    self.log.critical(f'There is an error with the CWM API request. (command = {command})')
            if command == 'server resume' and 'access denied' in str(output):
                self.log.critical(f'The server cannot be resumed because it has been suspended by the CWM administrator. (command = {command})')
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                self.log.exception(f"{self.logger.function_name()} json.JSONDecodeError")
        else:
            self.log.error(f"{self.logger.function_name()} {error}")
    
    def get_cwm_servers(self):
                servers_list = self.cwm_command(command='servers list')
                self.log.info('Sending API request to list the servers.')
                try: 
                    sorted_servers_list = [server for server in servers_list if server['name'].lower().startswith(self.global_servers['name'])]
                    return sorted_servers_list
                except KeyError: 
                    self.log.exception(f'{self.logger.function_name()} - KeyError')
                    exit()
                
    def update_haproxy_DB(self):
        cwm_servers = self.get_cwm_servers()
        haproxy_db_server = self.haDB.get_server_list()
        for server in cwm_servers:
            haproxy_DB_server_result =  self.haDB.get_server('server_id',server['id'])
            if haproxy_DB_server_result == None:
                self.add_server(server['id'])
            elif haproxy_DB_server_result == 'duplicated serves':
                self.haDB.delete_server(server['id'])
                self.add_server(server_id=server['id'])
            else:
                server_info = self.cwm_command(command='server info', server_id=server['id'])
                for ha_server in haproxy_db_server:
                    if server_info[0]['id'] == ha_server[1]:
                        ha_server_integrity_check = (
                                ha_server[0].lower() == server_info[0]['name'].lower(),
                                ha_server[2] == [ip if ip.startswith(self.global_servers['network']) else  server_info[0]['networks'][0]['ips'][0] for ip in server_info[0]['networks'][0]['ips']][0],
                                )
                        if server_info[0]['power'] != ha_server[5]:
                           self.haDB.update_server_data('server_id',server_info[0]['id'],'server_status',server_info[0]['power'])
                        if False in ha_server_integrity_check:
                            self.haDB.delete_server(server['id'])
                            self.add_server(server_id=server['id'])
                        if True in ha_server_integrity_check and False not in ha_server_integrity_check:
                            haproxy_db_server.remove(ha_server)
        if len(haproxy_db_server) > 0:
            for old_server in haproxy_db_server:
                self.log.info(f'Old server has been removed from the SERVERS table.( server name: {old_server})')
                self.haDB.delete_server(old_server[1])
    
    def add_server(self,server_id):
        self.log.info(f'Sending API request to retrieve server information. (server id: {server_id})')
        server_info = self.cwm_command(command='server info', server_id=server_id)
        try:
            server_data = {
                    'server_name': server_info[0]['name'],
                    'server_id': server_info[0]['id'],
                    'server_ip': [ip if ip.startswith(self.global_servers['network']) else server_info[0]['networks'][0]['ips'][0] for ip in server_info[0]['networks'][0]['ips']][0],
                    'server_sessions': '0',
                    'backend': 'backend_' + server_info[0]['name'].replace(self.global_servers['name']+'.', ''),
                    'server_status': server_info[0]['power'],
            }
            idle_time = self.idle_time[server_data['server_status']]
            self.haDB.update_server_list(server_data,idle_time)
        except KeyError:
            self.log.exception(f'{self.logger.function_name()} - Failed to add the server to the database and HAProxy due to an unexpected API response when retrieving server information. (server id: {server_id})')
   
    def start_server(self, backend):
        if 'backend' not in  backend: return None
        backend_name = backend.replace('\n','')
        server_id = self.haDB.get_server('backend',backend_name,'server_id')
        try:
            server_id = server_id[0]
            if server_id == None:
                self.log.error(f'{self.logger.function_name()} Failed to turn on the server because the server ID retrieved from the database is None. (backend: {backend_name})')
                self.update_haproxy_DB()
                return None
        except TypeError:
            self.log.error(f'{self.logger.function_name()} Failed to turn on the server because the server ID was not found in the database. (backend: {backend_name})')
            self.update_haproxy_DB()
            return None
        
        server_status = self.get_server_status(server_id)
        if server_status == 'on':
            self.log.info(f'Attempted to turn on the server but the server is already running. (server id: {server_id})')
            self.haDB.update_server_data('server_id',server_id,'server_status',server_status)
            self.haDB.update_server_data('server_id',server_id,'idle_time', self.idle_time[server_status])
        elif server_status == 'suspended':
            self.log.info(f'Sending API request to resume the server. (server id: {server_id})')
            self.power_on_server(server_id,'server resume')
        elif server_status == 'off':
            self.log.info(f'Sending API request to turn on the server. (server id: {server_id})')
            self.power_on_server(server_id,'server poweron')
        else:
            self.log.warning(f'{self.logger.function_name()} - Failed to turn on the server. The server is in an unexpected status. (server id: {server_id}, server status: {server_status})')

            
    def get_server_status(self,server_id):
        try:
            self.log.info(f'Sending API request to check the server status. (server id: {server_id})')
            return self.cwm_command(command='server info', server_id=server_id)[0]['power']
        except KeyError:
            self.log.exception(f'{self.logger.function_name()} - KeyError - Failed to retrieve the server status due to an unexpected API response. (server id: {server_id})')
            self.update_haproxy_DB()
            return None
    
    def power_on_server(self,server_id,action):
        self.cwm_command(command=action, server_id=server_id)
        sleep(self.sleep_checker)
        server_status = self.get_server_status(server_id)
        if server_status != None:
            self.haDB.update_server_data('server_id',server_id,'server_status',server_status)
            self.haDB.update_server_data('server_id',server_id,'idle_time',self.idle_time[server_status])

    def suspend_servers(self):
        for server_id in self.suspend_servers_list:
            self.log.info(f'Sending API request to suspend the server. (server id: {server_id})')
            self.cwm_command(command='server suspend', server_id=server_id)
        
        sleep(self.sleep_checker)
        for server_id in self.suspend_servers_list:
            server_status = self.get_server_status(server_id)
            if server_status != None:
                self.haDB.update_server_data('server_id',server_id,'server_status',server_status)
                self.haDB.update_server_data('server_id',server_id,'idle_time',self.idle_time[server_status])


    def sync_ha_config_file_backends(self):
        self.update_haproxy_DB()
        ha_config_file_backends = self.ha_api.backends_list()
        if ha_config_file_backends == None:
            self.log.warning(f'{self.logger.function_name()} The HAProxy configuration file does not contain any backend configurations.')
        ha_db_backends = self.haDB.get_backends()
        
        for backend in ha_db_backends.copy():
            try:
                if backend in ha_config_file_backends:
                    ha_config_file_backends.remove(backend)
                    ha_db_backends.remove(backend)
            except TypeError:
                self.log.exception(f'{self.logger.function_name()} - TypeError - please make sure that the haproxy service is running.')
                exit()
        for old_backend in ha_config_file_backends:
            self.log.info(f'Removing the old backend configuration from the HAProxy configuration. (old backend: {old_backend})')
            self.ha_api.delete_backend(old_backend)
        for new_backend in ha_db_backends:
            self.log.info(f'Adding a new backend to the HAProxy configuration. (backend: {new_backend})')
            backend_data = self.haDB.get_server('backend',new_backend)
            server_name,server_address = backend_data[0],backend_data[2]
            self.ha_api.add_backend(
                    backend_name = new_backend,
                    server_name = server_name,
                    server_address = server_address
                    )
    
    def update_server_state(self):
        cwm_status = self.cwm_command('servers list')
        db_status = {server[0]:server[-1] for server in self.haDB.get_server_list()}
        ha_status = self.ha_api.get_server_stats()
        for server in cwm_status:
            try:
                if server['power'] == 'on':
                    if ha_status[server['name'].lower()]['current_sessions'] <= 0:
                        self.haDB.update_server_data('server_name',server['name'],'server_sessions','0')
                        if 'minutes' in db_status[server['name']]:
                            idle_time = int(db_status[server['name']].split(' ')[0])

                            if (idle_time + self.idle_time['interval']) >= self.idle_time['timeout']:
                                self.suspend_servers_list.append(server['id'])
                        else:
                            self.haDB.update_server_data('server_id',server['id'],'idle_time',f"{self.idle_time['interval']} minutes")

                    elif db_status[server['name']] != self.idle_time[server['power']]:
                        self.haDB.update_server_data('server_name',server['name'],'idle_time',self.idle_time[server['power']])
                    else:
                        self.haDB.update_server_data('server_name',server['name'],'server_sessions',ha_status[server['name'].lower()]['current_sessions'])
                            
                elif server['power'] in ('off', 'suspended'):
                    if db_status[server['name']] != self.idle_time[server['power']]:
                        self.haDB.update_server_data('server_name',server['name'],'idle_time',self.idle_time[server['power']])

            except KeyError:
                self.log.exception(f'{self.logger.function_name()} - KeyError - Failed to update the server statistics in the database.')
    
    
    def find_rdp_cookie_name(self,server_name):
        seperator_char = self.global_servers['username'][self.global_servers['username'].find('username')-1]
        user_index = self.global_servers['username'].split(seperator_char).index('username')
        username = server_name.split(seperator_char)[user_index].lower()
        if len(username) > 9:
            return '^' + username[0:9]
        else:
            return username

    def update_maps(self):
        map_file = self.ha_api.get_map_file()
        map_entries = self.ha_api.get_map_entries(map_file)
        db_servers = {server[0]:server[4] for server in self.haDB.get_server_list()}
        db_maps = {map_key[0]:map_key[-1] for map_key in self.haDB.get_maps()}
        
        for server in db_servers:
            map_entry = self.find_rdp_cookie_name(server)
            if map_entry in map_entries and map_entry in db_maps:
                if db_servers[server] != db_maps[map_entry]: 
                    self.haDB.update_map(map_entry,db_servers[server])
                if db_servers[server] != map_entries[map_entry]: 
                    self.ha_api.add_map_entry(map_file,map_entry,db_servers[server])
                del db_maps[map_entry]
                del map_entries[map_entry]
            elif map_entry not in map_entries and map_entry not in db_maps:
                self.haDB.add_map(map_entry,db_servers[server])
                self.ha_api.add_map_entry(map_file,map_entry,db_servers[server])
            elif map_entry in map_entries and map_entry not in db_maps:
                if db_servers[server] != map_entries[map_entry]:
                    self.ha_api.add_map_entry(map_file,map_entry,db_servers[server])
                self.haDB.add_map(map_entry,db_servers[server])
                del map_entries[map_entry]
            elif map_entry in db_maps and map_entry not in map_entries:
                if db_servers[server] != db_maps[map_entry]: self.haDB.update_map(map_entry,db_servers[server])
                self.ha_api.add_map_entry(map_file,map_entry,db_servers[server])
                del db_maps[map_entry]
            else:
                self.log.error(f'{self.logger.function_name()} - Received an unexpected status for a map entry. (map key: {map_entry})')
        for old_entry in db_maps:
            self.log.info(f'Removing an old map entry from the maps database. (map key: {old_entry})')
            self.haDB.delete_map(old_entry)
        for old_entry in map_entries:
            self.log.info(f'Removing an old map entry from the haproxy maps file. (map key: {old_entry})')
            self.ha_api.delete_map_entry(map_file,old_entry)


       
