import netifaces


def get_host():
    iface = {}
    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface)
        ip_info = addrs.get(netifaces.AF_INET)
        if ip_info:
            for addr in ip_info:
                iface[interface]= addr['addr']
    return iface

