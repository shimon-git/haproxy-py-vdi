# PIP INSTALL REQUESTS
import requests
import json
import socket
from logger import Logger
class HaproxyApi():
    def __init__(self, username,password,host,port,backend_config):
        self.auth = (username,password)
        self.url = self.url = f"http://{host}:{port}/v2/services/haproxy/"
        self.mode = backend_config['mode']
        self.tcp_delay_inspection = int(backend_config['tcp_delay_inspection'])
        self.lua_action = backend_config['lua_action']
        self.connect_timeout = int(backend_config['connect_timeout'])
        self.server_timeout = int(backend_config['server_timeout'])
        self.server_port = int(backend_config['server_port'])
        self.logger =  Logger()
        self.log = self.logger.setup_logger()

    def socket_command(self,command):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as haproxy_socket:
                haproxy_socket.connect(('127.0.0.1', 9999))
                haproxy_socket.settimeout(5)
                haproxy_socket.sendall(command.encode())
                response = haproxy_socket.recv(4096).decode()
            return response
        except Exception:
            self.log.exception(f'{self.logger.function_name()} - make sure the haproxy service is running!')
            

    def backends_list(self):
        try: 
            backends = self.socket_command('show backend\n')
            self.log.info('The backend list has been successfully retrieved from the HAProxy configuration.')
            return [backend for backend in backends.split('\n')[1::] if backend not in (None, '', 'MASTER')]
        except Exception:
             self.log.exception(f'{self.logger.function_name()} - make sure the haproxy service is running!')


    def get_version(self):
        try:
            endpoint = self.url + 'configuration/version'
            r = requests.get(endpoint, auth=self.auth)
            return r.json()
        except Exception:
            self.log.exception(f'{self.logger.function_name()} - make sure the haproxy service and the dataplaneapi are running!')


    def delete_backend(self,backend):
        try:
            endpoint = self.url + 'configuration/backends/%s'%backend 
            params = {'version': self.get_version()}
            requests.delete(endpoint, auth=self.auth, params=params)
            self.log.info(f'Successfully deleted the backend from the HAProxy configuration. (backend: {backend})')
        except Exception:
            self.log.exception(f'{self.logger.function_name()} - make sure the haproxy service and the dataplaneapi are running!')

    def create_backend(self,backend_name):
        try:
            backend_config = {
                'name': backend_name,
                'mode': self.mode,
                'connect_timeout': int(self.connect_timeout),
                'server_timeout': int(self.server_timeout)
                }
            endpoint =self.url + 'configuration/backends'
            params = {'version': self.get_version()}
            requests.post(endpoint, json=backend_config,auth=self.auth,params=params)
        except Exception:
            self.log.exception(f'{self.logger.function_name()} - make sure the haproxy service and the dataplaneapi are running!')
        

    def set_tcp_lua_action(self,backend):
        try:
            endpoint = self.url+'configuration/tcp_request_rules'
            params = {'parent_name': backend, 'parent_type': 'backend', 'version': self.get_version()} 
            conf = {
                'lua_action': self.lua_action,
                'lua_params': backend,
                'type': 'content',
                'action': 'lua',
                'index': 1
            }
            requests.post(endpoint, json=conf,auth=self.auth,params=params)
        except Exception:
            self.log.exception(f'{self.logger.function_name()} - make sure the haproxy service and the dataplaneapi are running!')
        

    def set_tcp_delay_inspection(self,backend):
        try:
            endpoint = self.url + 'configuration/tcp_request_rules'
            params = {'parent_name': backend, 'parent_type': 'backend', 'version': self.get_version()}
            conf = {
                'timeout': int(self.tcp_delay_inspection),
                'type': 'inspect-delay',
                'index': 0
            }
            requests.post(endpoint, json=conf,auth=self.auth,params=params)
        except Exception:
            self.log.exception(f'{self.logger.function_name()} - make sure the haproxy service and the dataplaneapi are running!')


    def create_server(self,backend,server_name,server_address):
        try:
            endpoint = self.url + 'configuration/servers'
            params = {'version': self.get_version(), 'backend': backend}
            server_config = {
                    'name': server_name,
                    'address': server_address,
                    'port': int(self.server_port),
                    'check': 'enabled',
                    'health_check_port': int(self.server_port)
                    }
            requests.post(endpoint, json=server_config, params=params, auth=self.auth)
        except Exception:
            self.log.exception(f'{self.logger.function_name()} - make sure the haproxy service and the dataplaneapi are running!')

    
    def add_backend(self,backend_name,server_name,server_address):
        self.create_backend(backend_name)
        self.set_tcp_delay_inspection(backend_name)
        self.set_tcp_lua_action(backend_name)
        self.create_server(backend_name,server_name,server_address)
        self.log.info(f'Successfully added the backend to the HAProxy configuration.(backend: {backend_name})')

    def get_server_stats(self):
        try:
            results = {}
            endpoint = self.url + 'stats/native'
            params = {'type':'server'}
            r = requests.get(endpoint, auth=self.auth,params=params)
            if r.status_code >= 200 and r.status_code < 300:
                for server in r.json()[0]['stats']:
                    results[server['name']]={
                        'server_status': server['stats']['status'],
                        'current_sessions': server['stats']['scur']}
                self.log.info('Successfully retrieved the server statistics.')
                return results
        except Exception:
            self.log.exception(f'{self.logger.function_name()} - make sure the haproxy service and the dataplaneapi are running!')


    def get_map_file(self):
        try:
            endpoint = self.url + 'runtime/maps'
            r = requests.get(endpoint, auth=self.auth)
            self.log.info('Successfully retrieved the storage name of the map file.')
            return r.json()[0]['storage_name']
        except Exception:
            self.log.exception(f'{self.logger.function_name()} - make sure the haproxy service and the dataplaneapi are running!')

    def get_map_entries(self,map_file_name):
        try:
            endpoint = self.url + 'runtime/maps_entries'
            params = {'map': map_file_name}
            r = requests.get(endpoint, params=params, auth=self.auth)
            self.log.info('Successfully retrieved the map entries.')
            return {map_file['key']:map_file['value'] for map_file in r.json()}
        except Exception:
            self.log.exception(f'{self.logger.function_name()} - make sure the haproxy service and the dataplaneapi are running!')
    
    def add_map_entry(self,map_file_name,key,value):
        try:
            endpoint = self.url + 'runtime/maps_entries'
            params = {'map': map_file_name, 'force_sync': True}
            data = {'key':key,'value':value}
            requests.post(endpoint,json=data,params=params,auth=self.auth)
            self.log.info(f'Map entry added successfully. (map_key: {key})')
        except Exception:
            self.log.exception(f'{self.logger.function_name()} - make sure the haproxy service and the dataplaneapi are running!')

    def delete_map_entry(self,map_file,map_key):
        try:
            with open(r'/etc/haproxy/maps/%s'%map_file, 'r') as maps:
                maps_entries = maps.readlines()
                maps_entries_list = [{entry.split(' ')[0]: entry.split(' ')[-1].replace('\n', '')} for entry in maps_entries]
                for entry in maps_entries_list:
                    if map_key == list(entry.keys())[0]:
                        maps_entries.pop(maps_entries_list.index(entry))
                        break
            with open(r'/etc/haproxy/maps/%s'%map_file, 'w') as maps:
                maps.writelines(maps_entries)
            self.log.info(f'Map entry successfully deleted. (map: {map_key})')
        except Exception:
            self.log.exception(f'{self.logger.function_name()}')
