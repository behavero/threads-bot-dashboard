#!/bin/bash

echo "🚨 Cleaning up utun interfaces, DNS, and routing..."

# 1. List utun interfaces
echo "📡 Active utun interfaces:"
ifconfig | grep utun

# 2. Flush DNS
echo "🧹 Flushing DNS..."
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

# 3. Kill any background utun processes (if known)
echo "💣 Killing known VPN/network processes..."
for process in orbit orbitd AdGuardService Tunnelblick openvpn tailscaled outline-client wireguard-agent; do
    sudo pkill -f "$process"
done

# 4. Remove any existing utun routes (IPv6 ones)
echo "🗑️ Deleting default routes to utun interfaces..."
for i in {0..9}; do
    sudo route -n delete -inet6 default -interface utun$i 2>/dev/null
done

# 5. Display current routing table
echo "📍 Current default routes:"
netstat -nr | grep default

# 6. Confirm resolv.conf
echo "🧾 Current DNS config:"
cat /etc/resolv.conf

# 7. Ping test
echo "�� Testing connection with ping to 8.8.8.8 (Ctrl+C to stop)..."
ping 8.8.8.8
