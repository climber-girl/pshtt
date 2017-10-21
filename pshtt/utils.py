#!/usr/bin/env python

import contextlib
import os
import json
import errno
import csv
import logging
import datetime
import sys
import traceback
import re


def format_last_exception():
    """Display exception without re-throwing it."""
    exc_type, exc_value, exc_traceback = sys.exc_info()
    return "\n".join(traceback.format_exception(exc_type, exc_value, exc_traceback))


def mkdir_p(path):
    """
    mkdir -p in python, from:
    http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
    """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


def json_for(object):
    return json.dumps(object, sort_keys=True,
                      indent=2, default=format_datetime)


def write(content, destination, binary=False):
    parent = os.path.dirname(destination)
    if parent is not "":
        mkdir_p(parent)

    if binary:
        f = open(destination, 'bw')
    else:
        f = open(destination, 'w')  # no utf-8 in python 2
    f.write(content)
    f.close()


def format_datetime(obj):
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, str):
        return obj
    else:
        return None


def load_domains(domain_csv):
    """Load domains from a CSV, skip a header row"""
    domains = []
    with open(domain_csv) as csvfile:
        for row in csv.reader(csvfile):
            if (not row[0]) or (row[0].lower().startswith("domain")):
                continue

            row[0] = row[0].lower()

            domains.append(row[0])
    return domains


def configure_logging(debug=False):
    """Configure logging level, so logging.debug can hinge on --debug"""
    if debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(format='%(message)s', level=log_level)


def format_domains(domains):
    """
    Convert web server URLs and into domain only format

    Can accept a string for a single URL or a list of strings for multiple URLs
    """
    if isinstance(domains, str):
        domains = [domains]

    formatted_domains = []

    for domain in domains:
        # Replace a single instance of http://, https://, and www. if present.
        formatted_domains.append(re.sub("^(https?://)?(www\.)?", "", domain))

    return formatted_domains


def debug(message, divider=False):
    if divider:
        logging.debug("\n-------------------------\n")

    if message:
        logging.debug("%s\n" % message)


@contextlib.contextmanager
def smart_open(filename=None):
    """
    Context manager that can handle writing to a file or stdout

    Adapted from: https://stackoverflow.com/a/17603000
    """
    if filename is None:
        fh = sys.stdout
    else:
        fh = open(filename, 'w')

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()
