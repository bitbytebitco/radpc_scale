from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import json
import logging
from pathlib import Path
from socket import socket
import sys
from time import gmtime
from urllib.parse import urljoin

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# This prevents requests from logging an error about invalid SSL certs.
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logging.basicConfig(
    format="[%(asctime)s][%(levelname)s][%(name)s.%(funcName)s():%(lineno)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.INFO)
logging.Formatter.converter = gmtime

log = logging.getLogger(__name__)


def main():
    args = parse_args()

    log.info(f'Args: {args}')

    jwt = args.jwt
    if jwt is None:
        jwt = Path(args.jwt_path).read_text().strip()

    if args.command == 'reg':
        register_callback(args.cpap_url, jwt, args.callback_url, not args.ignore_ssl)
    elif args.command == 'test':
        test_callback(args.cpap_url, jwt, not args.ignore_ssl)
    elif args.command == 'check':
        check_callback(args.cpap_url, jwt, not args.ignore_ssl)


def register_callback(cpap_url, jwt, callback_url, verify_ssl=True):
    endpoint = urljoin(f'{cpap_url}/', 'callback')
    headers = {
        'Authorization': f'Bearer {jwt}'
    }

    data = json.dumps({
        'callback': callback_url
    })

    log.info(f'PUT {endpoint}')
    log.info(f'JWT: {jwt}')
    log.info(f'data: {data}')

    try:
        response = requests.put(endpoint, data=data, headers=headers, verify=verify_ssl, allow_redirects=False)
    except requests.exceptions.SSLError:
        log.error('Invalid SSL certificate. Pass the --ignore-ssl flag to ignore.')
        sys.exit(1)

    if response.status_code == requests.codes.found:
        log.error('Received 302 redirect. Did you use http instead of https?')
        sys.exit(1)

    log.info(f'Response: {response.status_code} - {response.text}')
    if not response.ok:
        log.error(f'Request failed with status code {response.status_code}')
        sys.exit(1)

    log.info('Success')


def check_callback(cpap_url, jwt, verify_ssl=True):
    endpoint = urljoin(f'{cpap_url}/', 'callback')
    headers = {
        'Authorization': f'Bearer {jwt}'
    }

    log.info(f'GET {endpoint}')
    log.info(f'JWT: {jwt}')

    try:
        response = requests.get(endpoint, headers=headers, verify=verify_ssl)
    except requests.exceptions.SSLError:
        log.error('Invalid SSL certificate. Pass the --ignore-ssl flag to ignore.')
        sys.exit(1)

    log.info(f'Response: {response.status_code} - {response.text}')
    if not response.ok:
        log.error(f'Request failed with status code {response.status_code}')
        sys.exit(1)


def test_callback(cpap_url, jwt, verify_ssl=True):
    endpoint = urljoin(f'{cpap_url}/', 'callback/test')

    headers = {
        'Content-Type': 'application/octet-stream',
        'Authorization': f'Bearer {jwt}',
    }

    data = 'This is a test!'

    log.info(f'PUT {endpoint}')
    log.info(f'JWT: {jwt}')
    log.info(f'data: {data}')

    try:
        response = requests.put(endpoint, data=data, headers=headers, verify=verify_ssl, allow_redirects=False)
        print(response)
        print(response.text)
    except requests.exceptions.SSLError:
        log.error('Invalid SSL certificate. Pass the --ignore-ssl flag to ignore.')
        sys.exit(1)

    if response.status_code == requests.codes.found:
        log.error('Received 302 redirect. Did you use http instead of https?')
        sys.exit(1)

    log.info(f'Response: {response.status_code} - {response.text}')
    if not response.ok:
        log.error(f'Request failed with status code {response.status_code}')
        sys.exit(1)

    log.info(f'Success')


def parse_args():
    ''' Parse commandline arguments '''
    # Arguments common to all the commands.
    common_args = ArgumentParser(add_help=False)
    common_args.add_argument('cpap_url', help='URL of the CPAP API service. (e.g. https://flights.ravenind.com/api/)')
    common_args.add_argument('--ignore-ssl', action='store_true', help='Ignore SSL cert errors. Use with caution.')
    jwt_group = common_args.add_mutually_exclusive_group()
    jwt_group.add_argument('--jwt-path', default='jwt.txt', help='Path to a file containing a JWT.')
    jwt_group.add_argument('--jwt', metavar='JWT', help='JWT as a string.')

    parser = ArgumentParser(description="Register callback server with CPAP", formatter_class=ArgumentDefaultsHelpFormatter)
    command_subparser = parser.add_subparsers(title='Commands', required=True, dest='command')

    register_parser = command_subparser.add_parser('reg', help='Register callback with CPAP', parents=[common_args], formatter_class=ArgumentDefaultsHelpFormatter)
    register_parser.add_argument('callback_url', help='Callback URL. Must be reachable from the CPAP server.')

    command_subparser.add_parser('test', help='Send a test callback from CPAP', parents=[common_args], formatter_class=ArgumentDefaultsHelpFormatter)

    command_subparser.add_parser('check', help='Check status of callback registration on CPAP', parents=[common_args], formatter_class=ArgumentDefaultsHelpFormatter)

    return parser.parse_args()


if __name__ == "__main__":
    main()
