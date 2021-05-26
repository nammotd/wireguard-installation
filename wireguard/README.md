## How to use
# Currently, support Ubuntu only
# Define necessary variables
[defaults/main.yml](defaults/main.yml)
```
wireguard_cidr: "10.0.1.0/24"
wireguard_public_ip: ""
network_interface: ['etho', 'eth1']
```

# Install
```
ansible-playbook -i hosts.ini playbooks/wireguard.yaml -v
```

# Add a new user
```
ansible-playbook -i hosts.ini playbooks/wireguard.yaml --tags add_users --extra-vars user=hainam -v
```
