import wgconfig
import wgconfig.wgexec as wgexec
from ipaddress import IPv4Address, IPv4Network
from jinja2 import Template
import sys

def get_latest_available_ip(wc_server, wireguard_cidr):
    list_peer = []
    all_peers = wc_server.peers.keys()
    vpn_cidr = IPv4Network(wireguard_cidr)
    for peer in all_peers:
        netip = wc_server.peers[peer]['AllowedIPs'].replace("/32", "")
        target = IPv4Address(netip)
        list_peer.append(target)
    if list_peer != []:
        latest = sorted(tuple(list_peer))[-1]
        for order, ip in enumerate(vpn_cidr):
            if ip == latest:
                result = vpn_cidr[order + 1]
    else:
        result = str(vpn_cidr[1])

    return str(result) + "/32"

def generate_client_conf(private, public, server_public, endpoint, address):
    config = Template("""
[Interface]
PrivateKey = {{ private }}
Address = {{ address }}
DNS = 1.1.1.1

[Peer]
PublicKey = {{ server_public }}
AllowedIPs = 0.0.0.0/0
Endpoint = {{ endpoint }}
PersistentKeepalive = 15
""")
    return config.render(private=private, public=public, server_public=server_public, endpoint=endpoint, address=address)

if __name__ == "__main__":
    ### Gather user input
    endpoint_port       = sys.argv[1]
    wireguard_path      = sys.argv[2]
    wireguard_interface = sys.argv[3]
    wireguard_cidr      = sys.argv[4]
    user_name           = sys.argv[5]

    ### Process information
    private, public = wgexec.generate_keypair()
    server_public = open(wireguard_path + "/pubkey", "r").read().strip("\n")
    wc_server = wgconfig.WGConfig(wireguard_interface)
    wc_server.read_file()
    latest_ip = get_latest_available_ip(wc_server, wireguard_cidr)

    ### Adjust server config
    wc_server.add_peer(public, '#{}'.format(user_name))
    wc_server.add_attr(public, 'AllowedIPs', latest_ip, append_as_line=True)
    wc_server.write_file()

    ### Generate client config
    with open(wireguard_path + "/keys/" + user_name + ".conf", "w") as f:
        client = generate_client_conf(private, public, server_public, endpoint_port, latest_ip)
        f.write(client)
