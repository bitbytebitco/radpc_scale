from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging
from pathlib import Path
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
    data = Path(args.data_path).read_text().strip()

    endpoint = urljoin(f'{args.cpap_url}/', f'flights/{args.flight_id}/payload/{args.payload_id}')

    headers = {
        'Content-Type': 'application/octet-stream',
        'Authorization': f'Bearer {jwt}'
    }

    log.info(f'PUT {endpoint}')
    log.info(f'JWT: {jwt}')
    log.info(f'Data: {data}')

    try:
        response = requests.put(endpoint, data=data, headers=headers, verify=not args.ignore_ssl, allow_redirects=False)
    except requests.exceptions.SSLError:
        log.error('Invalid SSL certificate. Pass the --ignore-ssl flag to ignore.')
        sys.exit(1)

    if response.status_code == requests.codes.found:
        log.error('Received 302 redirect. Did you use http instead of https?')
        sys.exit(1)

    log.info(f'Response: {response.status_code} - {response.text}')
    if not response.ok:
        log.info(f'Send failed with status code {response.status_code}')
        sys.exit(1)

    log.info('Success')


def parse_args():
    ''' Parse commandline arguments '''
    parser = ArgumentParser(description="Sends data to the payload via the CPAP API", formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('cpap_url', help='URL of the CPAP API service. (e.g. https://flights.ravenind.com/api/)')

    jwt_group = parser.add_mutually_exclusive_group()
    jwt_group.add_argument('--jwt-path', default='jwt.txt', help='Path to a file containing a JWT.')
    jwt_group.add_argument('--jwt', metavar='JWT', help='JWT.')

    parser.add_argument('--data-path', default='data.txt', help='Path to a file with the data to send to the payload.')
    parser.add_argument('--flight-id', type=int, default=1, help='Flight ID')
    parser.add_argument('--payload-id', type=int, default=1, help='Payload ID')
    parser.add_argument('--ignore-ssl', action='store_true', help='Ignore SSL cert errors. Use with caution.')

    return parser.parse_args()


if __name__ == "__main__":
    main()
