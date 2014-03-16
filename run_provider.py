#!/bin/env python3
import argparse

import log
from provider.file import File
from provider.journald import Journald


def main(loglevel, provider):
    log.init(loglevel)

    while True:
        log.logger.debug(provider.get_next())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LogEmperor provider')
    parser.add_argument(
        '-t',
        '--type',
        type=str,
        choices=('file', 'journald'),
        metavar='TYPE',
        action='store',
        help='LogEmperor provider type',
        required=True,
    )
    parser.add_argument(
        '-l',
        '--logfile',
        type=str,
        metavar='LOG_FILE',
        action='store',
        help='Log file to watch when using file provider',
    )
    parser.add_argument(
        '-d',
        '--debug',
        type=str,
        metavar='LOG_LEVEL',
        action='store',
        help='Loglevel',
        default='WARNING'
    )
    args = parser.parse_args()

    provider = None
    if args.type == 'file':
        if not args.logfile:
            parser.error('You must specify --logfile when using --type file')
        provider = File(args.logfile)
    elif args.type == 'journald':
        provider = Journald()

    main(args.debug, provider)
