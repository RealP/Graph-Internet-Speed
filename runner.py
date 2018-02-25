"""
Run SpeedTester repetitively with a specified delay and duration.

Details
-------
If you clear the process id file while the script is running it will stop the execution.
"""
import argparse
import logging
import os
import sys
import time

import SpeedTester


def parse_cmd_line_options():
    """Option parser for runner."""
    parser = argparse.ArgumentParser(prog='runner.py',
                                     description="Set script frequency and duration.",
                                     epilog="Both frequency and duration should be formatted as follows  ----------- interger [sec|min|hour|day|] ex) 5 min")
    parser.add_argument("-f", "--frequency", nargs=2, required=True,
                        help='How often should we run.')
    parser.add_argument("-d", "--duration", nargs=2, default=[24, "hour"],
                        help="How long should we run. (default=%(default)s)")
    parser.add_argument("-resultfile", default="Results/speedresults.txt")
    parser.add_argument("-configfile")
    parser.add_argument("-pidfile")
    return parser.parse_args()


def get_seconds(option):
    """
    Get seconds from command line option.

    @param a command line option.
    @retval integer seconds
    """
    sec_option = ["s", "sec", "secs"]
    min_option = ["m", "min", "mins"]
    hr_option = ["h", "hour", "hours"]
    day_option = ["d", "day", "days"]
    if option[1] in sec_option:
        return int(option[0])
    elif option[1] in min_option:
        return int(option[0]) * 60
    elif option[1] in hr_option:
        return int(option[0]) * 3600
    elif option[1] in day_option:
        return int(option[0]) * 216000
    else:
        sys.exit("Error {0} is not accepted".format(option[1]))


class Runner(object):
    """Used for proper teardown"""

    def __init__(self, exec_num, sec_delay, sec_to_run, start_time, tester, logger, pidfile=None):
        """
        Initialize Runner.

        @param exec_num
        @param sec_delay
        @param sec_to_run
        @param start_time
        @param tester
        @param logger a logger
        @param pidFile path to pid file (default:None)
                       You can stop the runner by overwriting its pidfile
        """
        super(Runner, self).__init__()
        self.exec_num = exec_num
        self.sec_delay = sec_delay
        self.sec_to_run = sec_to_run
        self.start_time = start_time
        self.tester = tester
        self.logger = logger
        self.pidfile = pidfile

        self.owns_pid = False

        # If we are instructed to use a process id file.
        if self.pidfile:
            # Verify the pidfile is blank before overwriting it.
            # We should stop the runner from starting if this happens.
            with open(self.pidfile, 'r') as f:
                if f.read():
                    self.logger.critical("PIDFILE IS NOT BLANK CANNOT START TEST!!!")
                    raise ValueError("pidfile must be blank before starting test!")

            # Looks like we own the file lets write our pid to it
            self.owns_pid = True
            with open(self.pidfile, 'w') as f:
                f.write(str(os.getpid()))

    def __del__(self):
        """Clean PID file."""
        self.logger.info("Tearing down runner")
        if self.pidfile and self.owns_pid:
            with open(self.pidfile, 'w') as f:
                f.write("")

    def we_should_stop(self):
        """Return True if pidfile is declared and blank."""
        if self.pidfile:
            with open(self.pidfile, 'r') as f:
                if f.read():
                    return False  # The file has data
                else:  # The file is declared but has no data
                    return True
        else:
            return False  # The file is not declared

    def run(self):
        while True:
            self.exec_num += 1
            self.logger.info ("""Execution number {exec_num}.\nElapsed secs = {time}"""
                   .format(exec_num=self.exec_num, time=time.time() - self.start_time))
            self.tester.run_test()
            self.tester.write_results_to_file(pretty=True)
            if self.we_should_stop():
                self.logger.info("runner was told to stop(pidfile blank)")
                break
            self.logger.info ("Done. now sleeping for {sec} second(s)".format(sec=self.sec_delay))
            time.sleep(self.sec_delay)
            if time.time() - self.start_time > float(self.sec_to_run):
                break


def main():
    """Run main function."""
    options = parse_cmd_line_options()
    sec_delay = get_seconds(options.frequency)
    sec_to_run = get_seconds(options.duration)
    start_time = time.time()
    exec_num = 0

    logging.basicConfig(level=logging.DEBUG)                   # Create a logger
    logger = logging.getLogger(__name__)                       # Any logger should do

    tester = SpeedTester.SpeedTester(logger, options.resultfile)
    tester.get_previous_results()
    runner = Runner(exec_num, sec_delay, sec_to_run, start_time, tester, logger, options.pidfile)
    runner.run()
    logger.close()

if __name__ == '__main__':
    main()
