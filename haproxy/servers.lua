local function turn_on_server(txn, name)
	-- create a tcp connection instance to 127.0.0.1:8888
				local conn = core.tcp()
				local server = "127.0.0.1"
				local port = 8888

				local connection, err = conn:connect(server,port)
				if not connection then
						core.Warning("Failed to connect to the python socket server: " .. err)
						return
				end
	-- sending the server name to the python socket which listening on 127.0.0.1:8888 --> the python socket responsible to turn on the server if the server is susspend of off
				local sent, err = conn:send(name)

				if not sent then
						core.Warning("Failed to send TCP request to the python socket server: " .. err)
						return
				end
				
	-- logging the information into the log file(/var/log/haproxy.log)
				for _, backend in pairs(core.backends) do
						if backend.name == name then
								core.Info('Login: ' .. name)
								for _, server in pairs(backend.servers) do
										repeat
												local stats = server:get_stats()
												core.Info(server.name ..' : ' .. stats['status'])
										until stats['status'] == 'UP'
								end

						end
				end

				
end
-- registraring the function so we can use it with the haproxy service.
core.register_action("turn_on_server", { "tcp-req" }, turn_on_server, 1)
