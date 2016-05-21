"""
@summary Runs a speed test to test internet speed.

Results are written to a file called "speedresults.txt" in a parent directory called Mgmt.
This script is best used on a cronjob or windows schedule.

@requirements Windows PC (NETSH)
              pip install speedtest-cli

@author Paul Pfeffer
"""

import os
import subprocess
import re
import json
import time

PATH_TO_RESULTS = os.path.dirname(os.path.realpath(__file__)) + "\speedresults.txt"
PATH_TO_RESULTS = PATH_TO_RESULTS.replace("Graph-Internet-Speed", "Mgmt")


def live_communicate(process, logger=None):
    """Execute subprocess printing data when available."""
    data_received = ""
    while True:
        line = process.stdout.readline()
        if line != '':
            if logger:
                logger.info(line.rstrip())
            else:
                print line.rstrip()
            data_received += line.rstrip()
        else:
            break
    return data_received


class SpeedTester(object):
    """Get the speed of Internet."""

    def __init__(self):
        """Define needed regex and main results dictionary."""
        super(SpeedTester, self).__init__()
        self.ipv4_regex = "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        self.results = {}

    def get_previous_results(self):
        """Add previous results from json."""
        with open(PATH_TO_RESULTS) as f:
            try:
                self.results = json.load(f)
            except ValueError:
                print "No json was loaded from speedresults.txt"

    def run_test(self):
        """Execute speed test process and save results."""
        print "Running Test.........."
        speedtest_process = subprocess.Popen(
            ["C:\Python27\Scripts\speedtest.exe"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        speedtest_out, er = speedtest_process.communicate()
        # speedtest_out = live_communicate(speedtest_process)

        speedtest_process = subprocess.Popen(
            ["NETSH", "WLAN", "SHOW", "INTERFACE", "|", "findstr", "/r", "'^....SSID'"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        wlan_info_out, err = speedtest_process.communicate()
        print "Running Test Complete."
        print "Saving Results"
        self.parse_and_save_results(speedtest_out + wlan_info_out)
        print "Saving Results Complete"

    def parse_and_save_results(self, output):
        """
        Parse results into the available keys.

        @param output the raw output from running speedtest.exe
        """
        # print output
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
            print "You have a wired connection"
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
        with open(PATH_TO_RESULTS, 'w') as f:
            if pretty:
                f.write(json.dumps(self.results, f, sort_keys=True, indent=4, separators=(',', ': ')))
            else:
                f.write(json.dumps(self.results, f))


def main():
    """Example of how to use the class."""
    tester = SpeedTester()
    tester.get_previous_results()
    tester.run_test()
    tester.write_results_to_file(pretty=True)

if __name__ == '__main__':
    main()
else:
    print __name__
