from servers import servers

def main():
    s = servers()
    s.sync_ha_config_file_backends()
    s.update_server_state()
    s.suspend_servers()
    s.update_maps()

if __name__ == '__main__':
    main()
