"""
Runs a speed test to test internet speed.

Results are written to a file called "speedresults.json" in a child directory called Results.
This script is best used with a cronjob, windows schedule or included runner script.

pip install speedtest-cli
"""
__author__ = "Paul Pfeffer"

import json
import os
import re
import subprocess
import time


def live_communicate(process, logger):
    """Execute subprocess printing data when available."""
    data_received = ""
    while True:
        line = process.stdout.readline()
        if line != '':
            logger.info(line.rstrip())
            data_received += line.rstrip()
        else:
            break
    return data_received


class SpeedTester(object):
    """Get the speed of Internet."""

    def __init__(self, logger, results_file):
        """Define needed regex and main results dictionary.

        @param logger
        @param results_file
        """
        super(SpeedTester, self).__init__()
        self.ipv4_regex = "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        self.results = {}
        self.logger = logger
        self.results_file = results_file
        if os.name == "nt":
            self.speedtest_cmd = "speedtest.exe"
        else:
            # assume nix
            self.speedtest_cmd = "speedtest-cli"

    def __del__(self):
        """Alert that class is being torn down."""
        self.logger.debug("Called __del__ method of SpeedTester")

    def get_previous_results(self):
        """Add previous results from json."""
        with open(self.results_file) as f:
            try:
                self.results = json.load(f)
            except ValueError:
                self.logger.critical("No json was loaded from speedresults.json")

    def run_test(self):
        """Execute speed test process and save results."""
        self.logger.info("Running Test..........")
        speedtest_process = subprocess.Popen(
            self.speedtest_cmd,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        speedtest_out = live_communicate(speedtest_process, logger=self.logger)

        if os.name == "nt":
            speedtest_process = subprocess.Popen(
                ["NETSH", "WLAN", "SHOW", "INTERFACE", "|", "findstr", "/r", "'^....SSID'"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            wlan_info_out, err = speedtest_process.communicate()
            speedtest_out += wlan_info_out

        self.logger.info("Running Test Complete.")
        self.logger.info("Saving Results")
        self.parse_and_save_results(speedtest_out)
        self.logger.info("Saving Results Complete")

    def parse_and_save_results(self, output):
        """
        Parse results into the available keys.

        @param output the raw output from running speedtest.exe
        """
        from_regex = "Testing from (.+) \((%s)" % self.ipv4_regex
        from_addr = re.search(from_regex, output)
        provider = from_addr.group(1)
        ip_addr = from_addr.group(2)
        ping_regex = "Hosted by.+?(\d+?.\d+?\sms)"
        ping_time = re.search(ping_regex, output).group(1)
        download_regex = "Download: (.+?/s)"
        download_speed = re.search(download_regex, output).group(1)
        upload_regex = "Upload: (.+?/s)"
        upload_speed = re.search(upload_regex, output).group(1)

        try:
            ssid_regex = "SSID\s+: (.+\s)"
            ssid_name = re.search(ssid_regex, output).group(1).strip()
        except AttributeError:
            self.logger.info("You have a wired connection")
            ssid_name = "wired"
        result = {
            "Provider": provider,
            "ip_address": ip_addr,
            "ping": ping_time,
            "download": download_speed,
            "upload": upload_speed,
            "ssid": ssid_name,
            "all_info": output
        }
        self.results[time.strftime("%Y-%m-%d %H:%M:%S")] = result

    def write_results_to_file(self, pretty=False):
        """
        Write the gathered results to a text file.

        @param pretty should be True if you want to read the result file yourself. (default=False)
        """
        with open(self.results_file, 'w') as f:
            if pretty:
                f.write(json.dumps(self.results, f, sort_keys=True, indent=4, separators=(',', ': ')))
            else:
                f.write(json.dumps(self.results, f))


def main():
    """Example of how to use the class."""
    import logging

    logging.basicConfig(level=logging.DEBUG)                   # Create a logger
    logger = logging.getLogger(__name__)                       # Any logger should do

    tester = SpeedTester(logger, "Results/speedresults.json")   # Create instance of class
    tester.get_previous_results()                              # Optionally load previous results
    tester.run_test()                                          # Run the tests
    tester.write_results_to_file(pretty=True)                  # Save results

if __name__ == '__main__':
    main()
