#!/usr/bin/env python3
"""Add GitHub Pages DNS records to Cloudflare zone calpinlabs.com"""
import json, subprocess
tok = open('/home/ryancalpin/.config/.wrangler/config/default.toml').read()
tok = tok.split('oauth_token = "')[1].split('"')[0]
zone = 'c871f86b8dbd82e136eb94a36c9dd740'
hdr = 'Bearer ' + tok

# Delete existing apex records (A, AAAA, CNAME for @)
r = subprocess.run(['curl', '-s', 'https://api.cloudflare.com/client/v4/zones/' + zone + '/dns_records', '-H', 'Authorization: ' + hdr], capture_output=True, text=True)
d = json.loads(r.stdout)
for rec in d.get('result', []):
    name = rec['name'].replace('.calpinlabs.com', '') or '@'
    if rec['type'] in ('A', 'AAAA', 'CNAME') and name == '@':
        subprocess.run(['curl', '-s', '-X', 'DELETE', 'https://api.cloudflare.com/client/v4/zones/' + zone + '/dns_records/' + rec['id'], '-H', 'Authorization: ' + hdr], capture_output=True, text=True)
        print('removed', rec['type'], rec['content'])

# Add 4 A records for GitHub Pages
ips = ['185.199.108.153', '185.199.109.153', '185.199.110.153', '185.199.111.153']
for ip in ips:
    body = '{"type":"A","name":"@","content":"' + ip + '","ttl":120,"proxied":false}'
    r = subprocess.run(['curl', '-s', '-X', 'POST', 'https://api.cloudflare.com/client/v4/zones/' + zone + '/dns_records', '-H', 'Authorization: ' + hdr, '-H', 'Content-Type: application/json', '-d', body], capture_output=True, text=True)
    d = json.loads(r.stdout)
    print('A', ip, '→', d.get('success'))