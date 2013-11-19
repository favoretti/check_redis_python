#!/usr/bin/python

import sys
import argparse
import redis
import pprint


def _nagios(hdr, msg, code):
    print '%s: %s' % (hdr, msg)
    return code


def critical(msg):
    return _nagios('CRITICAL', msg, 2)


def warning(msg):
    return _nagios('WARNING', msg, 1)


def okay(msg):
    return _nagios('OK', msg, 0)


def check_stat_value(_redis, db, stat, crit, warn):
    stats = _redis.info()
    value = None
    dbkey = "db{0}".format(db)

    if dbkey in stats.keys():
        if stat in stats[dbkey].keys():
            value = stats[dbkey][stat]

    if not value and stat in stats.keys():
        value = stats[stat]

    if not value:
        return critical("{0} is not a valid metric".format(stat))

    if not isinstance(value, float):
        return critical("{0} returned non numerical value: {1}".format(stat, value))

    if value >= float(crit):
        return critical("{0} exceeds critical level ({1}): {2}".format(stat, crit, value))
    elif value >= float(warn):
        return warning("{0} exceeds warning level ({1}): {2}".format(stat, warn, value))
    else:
        return okay("{0} is ok. {0}={1}".format(stat, value))

def main(args):

    parser = argparse.ArgumentParser(description="Redis monitor")
    parser.add_argument('--warn', '-w', metavar='NUM_WARN', type=float, required=True, help='Warning level')
    parser.add_argument('--crit', '-c', metavar='NUM_CRIT', type=float, required=True, help='Critical level')
    parser.add_argument('--host', '-H', metavar='HOST', default='localhost', help='Hostname')
    parser.add_argument('--port', '-p', metavar='PORT', type=int, default=6379, help='Port')
    parser.add_argument('--password', '-P', metavar='PASSWORD', help='Password')
    parser.add_argument('--timeout', '-t', metavar='TIMEOUT', type=int, default=5, help='Connection timeout in seconds')
    parser.add_argument('--stat', '-s', metavar='STAT', required=True, help='Stat to check')
    parser.add_argument('--db', '-d', metavar='DB', type=int, help='Perform stat query on particular database statistics')
    args = parser.parse_args()

    _redis = redis.Redis(host=args.host, port=args.port, db=args.db, password=args.password, socket_timeout=args.timeout)
    return check_stat_value(_redis, args.db, args.stat, args.crit, args.warn)


if __name__ == "__main__":
    sys.exit(main(sys.argv[0:]))
