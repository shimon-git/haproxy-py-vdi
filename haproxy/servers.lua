local function turn_on_server(txn, name)
    -- Create a TCP connection instance to 127.0.0.1:8888
    local conn = core.tcp()
    local server = "127.0.0.1"
    local port = 8888

    -- Connect to the Python socket server
    local connection, err = conn:connect(server, port)
    if not connection then
        core.Warning("Failed to connect to the Python socket server: " .. err)
        return
    end

    -- Send the server name to the Python socket server
    local sent, err = conn:send(name)
    if not sent then
        core.Warning("Failed to send TCP request to the Python socket server: " .. err)
        return
    end

    -- Log the server status information into the log file (/var/log/haproxy.log)
    for _, backend in pairs(core.backends) do
        if backend.name == name then
            core.Info('Logging: ' .. name)
            for _, server in pairs(backend.servers) do
                while true do
                    local stats = server:get_stats()
                    core.Info(server.name .. ' : ' .. stats['status'])
                    if stats['status'] == 'UP' then break end
                end
            end
        end
    end
end

-- Register the function so it can be used with the HAProxy service
core.register_action("turn_on_server", { "tcp-req" }, turn_on_server, 1)
