#!/bin/env python3
import argparse
import configparser
import os
import sys
import time
import log

from worker.worker import Worker


def main(config):
    log.init(config.get('worker', 'log_level'))

    w = Worker(config.get('worker', 'server_at'))
    w.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run LogEmperor Worker')
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
