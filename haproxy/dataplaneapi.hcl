config_version = 2

name = "training.it.shimon-haproxy-rdp"

mode = "single"

dataplaneapi {
  host       = "0.0.0.0"
  port       = 5555
  advertised = {}

  scheme = ["http"]

  transaction {
    transaction_dir = "/tmp/haproxy"
  }

  user "admin" {
    insecure = true
    password = "adminpwd"
  }
}

haproxy {
  config_file = "/etc/haproxy/haproxy.cfg"
  haproxy_bin = "/usr/sbin/haproxy"

  reload {
    reload_delay    = 5
    reload_cmd      = "service haproxy reload"
    restart_cmd     = "service haproxy restart"
    reload_strategy = "custom"
  }
}
