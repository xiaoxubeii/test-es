#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'tardis'

from locust import runners, events, TaskSet
from locust.runners import LocalLocustRunner
from optparse import OptionParser
from locust.stats import print_percentile_stats, print_error_report, print_stats, stats_printer
import gevent
import sys
import signal
from testes import CONF
from testes.main_test import MainTest
from locust.log import setup_logging
import os
import inspect


def parse_options():
    """
    Handle command-line options with optparse.OptionParser.

    Return list of arguments, largely for use in `parse_arguments`.
    """

    # Initialize
    parser = OptionParser(usage="locust [options] [LocustClass [LocustClass2 ... ]]")

    parser.add_option(
        '-H', '--host',
        dest="host",
        default=None,
        help="Host to load test in the following format: http://10.21.32.33"
    )

    parser.add_option(
        '--web-host',
        dest="web_host",
        default="",
        help="Host to bind the web interface to. Defaults to '' (all interfaces)"
    )

    parser.add_option(
        '-P', '--port', '--web-port',
        type="int",
        dest="port",
        default=8089,
        help="Port on which to run web host"
    )

    parser.add_option(
        '-f', '--locustfile',
        dest='locustfile',
        default='locustfile',
        help="Python module file to import, e.g. '../other.py'. Default: locustfile"
    )

    # if locust should be run in distributed mode as master
    parser.add_option(
        '--master',
        action='store_true',
        dest='master',
        default=False,
        help="Set locust to run in distributed mode with this process as master"
    )

    # if locust should be run in distributed mode as slave
    parser.add_option(
        '--slave',
        action='store_true',
        dest='slave',
        default=False,
        help="Set locust to run in distributed mode with this process as slave"
    )

    # master host options
    parser.add_option(
        '--master-host',
        action='store',
        type='str',
        dest='master_host',
        default="127.0.0.1",
        help="Host or IP address of locust master for distributed load testing. Only used when running with --slave. Defaults to 127.0.0.1."
    )

    parser.add_option(
        '--master-port',
        action='store',
        type='int',
        dest='master_port',
        default=5557,
        help="The port to connect to that is used by the locust master for distributed load testing. Only used when running with --slave. Defaults to 5557. Note that slaves will also connect to the master node on this port + 1."
    )

    parser.add_option(
        '--master-bind-host',
        action='store',
        type='str',
        dest='master_bind_host',
        default="*",
        help="Interfaces (hostname, ip) that locust master should bind to. Only used when running with --master. Defaults to * (all available interfaces)."
    )

    parser.add_option(
        '--master-bind-port',
        action='store',
        type='int',
        dest='master_bind_port',
        default=5557,
        help="Port that locust master should bind to. Only used when running with --master. Defaults to 5557. Note that Locust will also use this port + 1, so by default the master node will bind to 5557 and 5558."
    )

    # if we should print stats in the console
    parser.add_option(
        '--no-web',
        action='store_true',
        dest='no_web',
        default=False,
        help="Disable the web interface, and instead start running the test immediately. Requires -c and -r to be specified."
    )

    # Number of clients
    parser.add_option(
        '-c', '--clients',
        action='store',
        type='int',
        dest='num_clients',
        default=1,
        help="Number of concurrent clients. Only used together with --no-web"
    )

    # Client hatch rate
    parser.add_option(
        '-r', '--hatch-rate',
        action='store',
        type='float',
        dest='hatch_rate',
        default=1,
        help="The rate per second in which clients are spawned. Only used together with --no-web"
    )

    # Number of requests
    parser.add_option(
        '-n', '--num-request',
        action='store',
        type='int',
        dest='num_requests',
        default=None,
        help="Number of requests to perform. Only used together with --no-web"
    )

    # log level
    parser.add_option(
        '--loglevel', '-L',
        action='store',
        type='str',
        dest='loglevel',
        default='INFO',
        help="Choose between DEBUG/INFO/WARNING/ERROR/CRITICAL. Default is INFO.",
    )

    # log file
    parser.add_option(
        '--logfile',
        action='store',
        type='str',
        dest='logfile',
        default=None,
        help="Path to log file. If not set, log will go to stdout/stderr",
    )

    # if we should print stats in the console
    parser.add_option(
        '--print-stats',
        action='store_true',
        dest='print_stats',
        default=False,
        help="Print stats in the console"
    )

    # only print summary stats
    parser.add_option(
        '--only-summary',
        action='store_true',
        dest='only_summary',
        default=False,
        help='Only print the summary stats'
    )

    # List locust commands found in loaded locust files/source files
    parser.add_option(
        '-l', '--list',
        action='store_true',
        dest='list_commands',
        default=False,
        help="Show list of possible locust classes and exit"
    )

    # Display ratio table of all tasks
    parser.add_option(
        '--show-task-ratio',
        action='store_true',
        dest='show_task_ratio',
        default=False,
        help="print table of the locust classes' task execution ratio"
    )
    # Display ratio table of all tasks in JSON format
    parser.add_option(
        '--show-task-ratio-json',
        action='store_true',
        dest='show_task_ratio_json',
        default=False,
        help="print json data of the locust classes' task execution ratio"
    )

    # Version number (optparse gives you --version but we have to do it
    # ourselves to get -V too. sigh)
    parser.add_option(
        '-V', '--version',
        action='store_true',
        dest='show_version',
        default=False,
        help="show program's version number and exit"
    )

    # Finalize
    # Return three-tuple of parser + the output from parse_args (opt obj, args)
    opts, args = parser.parse_args()
    return parser, opts, args


def shutdown(code=0):
    """
    Shut down locust by firing quitting event, printing stats and exiting
    """
    events.quitting.fire()
    print_stats(runners.locust_runner.request_stats)
    print_percentile_stats(runners.locust_runner.request_stats)

    print_error_report()
    sys.exit(code)


# install SIGTERM handler
def sig_term_handler():
    shutdown(0)


def timer(greenlet):
    gevent.sleep(float(CONF.interval))
    runners.locust_runner.locusts.kill()
    gevent.kill(greenlet)


def log(curr_class, curr_task):
    gevent.sleep(float(CONF.log_interval))
    _log_stats(curr_class, curr_task)


STATS_NAME_WIDTH = 60


def _log_stats(curr_testcase, curr_task):
    stats = runners.locust_runner.request_stats

    def _print_stats():
        log = (" %-" + str(STATS_NAME_WIDTH) + "s %7s %12s %7s %7s %7s  | %7s %7s\n") % (
            'Name', '# reqs', '# fails', 'Avg', 'Min', 'Max', 'Median', 'req/s')
        log += "-" * (80 + STATS_NAME_WIDTH) + '\n'
        total_rps = 0
        total_reqs = 0
        total_failures = 0
        for key in sorted(stats.iterkeys()):
            r = stats[key]
            total_rps += r.current_rps
            total_reqs += r.num_requests
            total_failures += r.num_failures
            log += str(r) + '\n'
        log += "-" * (80 + STATS_NAME_WIDTH) + '\n'

        try:
            fail_percent = (total_failures / float(total_reqs)) * 100
        except ZeroDivisionError:
            fail_percent = 0

        log += (" %-" + str(STATS_NAME_WIDTH) + "s %7d %12s %42.2f\n") % (
            'Total', total_reqs, "%d(%.2f%%)\n" % (total_failures, fail_percent), total_rps)

        return log

    test_logfile = '%s/%s_%s' % (CONF.test_logfile_dir, curr_testcase.__name__.lower(), curr_task.func_name)
    with open(test_logfile, 'a+') as f:
        f.write(_print_stats())


def run(test_case, options):
    try:
        for t in test_case.tasks:
            test_case.tasks = [t]
            MainTest.task_set = test_case
            runners.locust_runner = LocalLocustRunner([MainTest], options)
            runners.locust_runner.start_hatching(wait=True)
            main_greenlet = runners.locust_runner.greenlet
            main_greenlet.spawn(timer, main_greenlet)
            main_greenlet.spawn(log, test_case, t)
            main_greenlet.join()
    except KeyboardInterrupt as e:
        shutdown(0)


def load_testcase(path):
    """
    Import given locustfile path and return (docstring, callables).

    Specifically, the locustfile's ``__doc__`` attribute (a string) and a
    dictionary of ``{'name': callable}`` containing all callables which pass
    the "is a Locust" test.
    """
    # Get directory and locustfile name
    directory, locustfile = os.path.split(path)
    # If the directory isn't in the PYTHONPATH, add it so our import will work
    added_to_path = False
    index = None
    if directory not in sys.path:
        sys.path.insert(0, directory)
        added_to_path = True
    # If the directory IS in the PYTHONPATH, move it to the front temporarily,
    # otherwise other locustfiles -- like Locusts's own -- may scoop the intended
    # one.
    else:
        i = sys.path.index(directory)
        if i != 0:
            # Store index for later restoration
            index = i
            # Add to front, then remove from original position
            sys.path.insert(0, directory)
            del sys.path[i + 1]
    # Perform the import (trimming off the .py)
    imported = __import__(os.path.splitext(locustfile)[0])
    # Remove directory from path if we added it ourselves (just to be neat)
    if added_to_path:
        del sys.path[0]
    # Put back in original index if we moved it
    if index is not None:
        sys.path.insert(index + 1, directory)
        del sys.path[0]
    # Return our two-tuple
    test_case = dict(filter(is_testcase, vars(imported).items()))
    return test_case


def is_testcase(tup):
    """
    Takes (name, object) tuple, returns True if it's a public Locust subclass.
    """
    name, item = tup
    return bool(
        inspect.isclass(item)
        and issubclass(item, TaskSet)
        and not name.startswith('_')
        and not name == 'TaskSet'
    )


def main():
    args = ['--no-web', '-c', CONF.client, '--hatch-rate', CONF.client]
    sys.argv.extend(args)
    parser, options, arguments = parse_options()
    setup_logging(options.loglevel, options.logfile)

    file_dir = CONF.test_file_dir
    test_cases = []
    for f in CONF.test_file_names.split(','):
        path = os.path.join(file_dir, f)
        cases = load_testcase(path)
        test_cases.append(cases)

    for case in test_cases:
        for k, v in case.iteritems():
            run(v, options)

    gevent.signal(signal.SIGTERM, sig_term_handler)


if __name__ == '__main__':
    main()
