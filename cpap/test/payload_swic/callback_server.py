import logging
from time import gmtime

from flask import Flask, Blueprint, request

logging.basicConfig(
    format="[%(asctime)s][%(levelname)s][%(name)s.%(funcName)s():%(lineno)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.INFO)
logging.Formatter.converter = gmtime

log = logging.getLogger(__name__)

bp = Blueprint('callback', __name__)


@bp.route('/callback', methods=['GET', 'PUT'])
def callback():
    log.info(f'{request.method} called on callback service')
    if request.method == 'PUT':

        data = request.data.decode('utf-8')

        # This is a little hack to allow us to test CPAP callbacks from within the DMZ by
        # running this service on the same server as CPAP.
        _send_test_msg(data)

        log.info(f'body: {data}')
        return request.data
    if request.method == 'GET':
        return 'Callback server is running.'


def _send_test_msg(data):
    ''' Send a test message to a MS Teams channel.

    Requires CPAP_TEST_TEAMS_URL environment variable be set to a valid Teams webhook url.
    '''
    # Wrap everything in a try block so it is ignored if running without
    # the Teams URL configured or pymsteams installed.
    try:
        import os
        import pymsteams
        url = os.environ['CPAP_TEST_TEAMS_URL']
        card = pymsteams.connectorcard(url)
        card.title("CPAP Callback Test")
        card.text(data)
        card.send()
    except:
        pass


def main():
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()
