"""Used to stop a process from a pidfile."""
import os
import argparse
import signal


def parse_cmd_line_options():
    """Option parser for stop_runner."""
    parser = argparse.ArgumentParser(prog='stop_runner.py',
                                     description="Stop process from pid.",
                                     epilog="Choose either pid or pidfile")
    parser.add_argument("-pid")
    parser.add_argument("-pidfile")
    return parser.parse_args()


def main():
    """."""
    options = parse_cmd_line_options()

    if options.pidfile:
        with open(options.pidfile, 'r') as f:
            os.kill(int(f.read().strip()), signal.SIGTERM)
    if options.pid:
        os.kill(options.pid, signal.SIGTERM)

if __name__ == '__main__':
    main()
