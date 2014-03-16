#!/bin/env python3
import argparse
import configparser
import os
import sys
import time
import log

from server.worker_master import WorkerMaster
from server.provider_master import ProviderMaster


def main(config):
    log.init(config.get('server', 'log_level'))

    wm = WorkerMaster(config.get('server', 'worker_listen'), filters=config.get('filters', 'regex').split('\n'))
    pm = ProviderMaster(config.get('server', 'provider_listen'), worker_master=wm)
    try:
        wm.run()
        pm.run()
    except KeyboardInterrupt:
        wm.stop()
        pm.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run LogEmperor')
    parser.add_argument(
        '-c',
        '--config',
        type=str,
        metavar='CONFIG_FILE',
        action='store',
        default='logemperor.ini',
        help='specify config file'
    )
    args = parser.parse_args()

    if not os.path.isfile(args.config) or not os.access(args.config, os.R_OK):
        print ("Config file \"%s\" is not readable!" % args.config, file=sys.stderr)
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(args.config)

    main(config)
