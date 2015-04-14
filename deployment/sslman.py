#!/usr/bin/env python3
from datetime import datetime, timedelta
import dateutil.parser
import subprocess
import copy
import os
import sys
import shutil
import yaml

vault_key = os.path.expanduser('~/.ansible_pass')

ansible_dir = os.path.realpath(os.path.curdir)
key_vault_path = os.path.join(ansible_dir, 'ssl_keys.vault')
queue_vault_path = os.path.join(ansible_dir, 'ssl_keys_queue.vault')

empty_key_vault = { 'ssl_keys': {} }
empty_queue_vault = []

def read_vault(path, default={}):
    if not os.path.exists(path):
        return copy.deepcopy(default)

    shutil.copy(path, '/tmp/temp.vault')
    with open(os.devnull, 'wb') as FNULL:
        ret = subprocess.call([
            'ansible-vault', '--vault-password-file=' + vault_key,
            'decrypt', '/tmp/temp.vault'
        ], stdout=FNULL)
    if ret != 0:
        sys.exit(1)

    with open('/tmp/temp.vault', 'r') as f:
        vault = yaml.load(f.read())

    return vault

def write_vault(vault, path):
    with open('/tmp/temp.vault', 'w') as f:
        f.write(yaml.dump(vault))

    with open(os.devnull, 'wb') as FNULL:
        ret = subprocess.call([
            'ansible-vault', '--vault-password-file=' + vault_key,
            'encrypt', '/tmp/temp.vault'
        ], stdout=FNULL)
    if ret != 0:
        print('Error encrypting the vault')
        sys.exit(1)

    with open('/tmp/temp.vault', 'rb') as sf:
        with open(path, 'wb') as df:
            df.write(sf.read())

def openssl_date(strdate):
    return datetime.strptime(strdate, '%b %d %H:%M:%S %Y %Z')

def cert_info(certificate):
    proc = subprocess.Popen([
        'openssl', 'x509', '-out', '/dev/null',
        '-dates'
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = proc.communicate(certificate.encode())
    if proc.returncode != 0:
        sys.exit(1)

    output = out.decode().split('\n')

    not_before = [openssl_date(line.split('=')[1])
                  for line in output if line.startswith('notBefore=')][0]
    not_after = [openssl_date(line.split('=')[1])
                 for line in output if line.startswith('notAfter=')][0]

    return not_before, not_after

def add_key(vault, site_name, certificate, private, ca):
    not_before, not_after = cert_info(certificate)

    if site_name in vault['ssl_keys']:
        site = vault['ssl_keys'][site_name]

        old_current = site['current']
        site[old_current['not_before']] = old_current
    else:
        site = vault['ssl_keys'][site_name] = {}

    new_pair = {
        'certificate': certificate,
        'private_key': private,
        'ca': ca,
        'not_before': not_before.strftime('%Y-%m-%d'),
        'not_after': not_after.strftime('%Y-%m-%d'),
    }
    site['current'] = new_pair

def read_cert_and_private():
    certificate_buf = []
    private_buf = []
    state = 'none'
    try:
        while True:
            line = input()
            if '-BEGIN CERTIFICATE-' in line:
                state = 'reading_certificate'
            elif '-BEGIN RSA PRIVATE KEY-' in line:
                state = 'reading_private'

            if state == 'reading_certificate':
                certificate_buf.append(line)
            elif state == 'reading_private':
                private_buf.append(line)

            # This check is done after appending, so tails are added to buffers too
            if '-END ' in line:
                state = 'none'
    except EOFError:
        if len(certificate_buf) == 0 or len(private_buf) == 0:
            print('You did not provide a certificate and a private key.')
            sys.exit(1)

    certificate = '\n'.join(certificate_buf)
    private = '\n'.join(private_buf)
    return certificate, private

from argparse import ArgumentParser

parser = ArgumentParser(description=
        "Queries and updates an SSL key vault.")
parser.add_argument("-l", "--list", dest="list", action="store_true",
                    help='Queries current keys')
parser.add_argument("-a", "--add", dest="add", metavar='SITE', nargs=1,
                    help='Adds a new key for a site (read it from stdin)')
parser.add_argument("-e", "--enqueue", dest="queue", metavar='SITE', nargs=1,
                    help='Queues a certificate for addition (read it from stdin)')
parser.add_argument("-u", "--update", dest="update", action="store_true",
                    help='Updates key vault with keys found in the queue file')
parser.add_argument("-C", "--ca", dest="ca", nargs='?', default='startssl',
                    help='Certification authority name')

args = parser.parse_args()

if args.list:
    vault = read_vault(key_vault_path, empty_key_vault)
    for site, key_pairs in sorted(vault['ssl_keys'].items(),
                                  key=lambda x: x[1]['current']['not_after']):
        if 'current' in key_pairs:
            print(site)
            print('  %s until %s' % (
                key_pairs['current']['not_before'],
                key_pairs['current']['not_after'],
            ))
            older_key_pairs = [id for id, kp in key_pairs.items()
                               if id != 'current']
            if len(older_key_pairs) > 0:
                print('  Older keys: %s' % ', '.join(older_key_pairs))
        else:
            print('%20s Invalid site D:' % site)
elif args.add:
    site = args.add[0]
    print('Write certificate and private key for %s:' % site)
    certificate, private = read_cert_and_private()

    vault = read_vault(key_vault_path, empty_key_vault)
    add_key(vault, site, certificate, private, args.ca)
    write_vault(vault, key_vault_path)
elif args.queue:
    site = args.queue[0]
    certificate, private = read_cert_and_private()

    queue = read_vault(queue_vault_path, empty_queue_vault)
    queue.append({
        'due_date': (datetime.now() + timedelta(days=1)).isoformat(),
        'site': site,
        'ca': args.ca,
        'certificate': certificate,
        'private': private,
    })
    write_vault(queue, queue_vault_path)
elif args.update:
    queue = read_vault(queue_vault_path, empty_queue_vault)
    remaining_queue = []
    vault = None

    for task in queue:
        if datetime.now() < dateutil.parser.parse(task['due_date']):
            remaining_queue.append(task)
        else:
            print('Adding certificate for %s...' % task['site'])
            if vault is None:
                vault = read_vault(key_vault_path, empty_key_vault)
            add_key(vault, task['site'], task['certificate'],
                    task['private'], task['ca'])

    if vault is not None:
        write_vault(vault, key_vault_path)
        write_vault(remaining_queue, queue_vault_path)
        print('Key vault updated.')
        sys.exit(0)
    else:
        print('Nothing to add.')
        sys.exit(2)
else:
    parser.print_help()
