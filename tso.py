import argparse
import threading
from subprocess import Popen, PIPE
from typing import List


def run_process(process_args: List):
    """
    Runs a python process and prints the stderr to the current console
    Args:
        process_args: The args to pass through to the process
    """
    process = Popen(process_args, stderr=PIPE, universal_newlines=True)

    while True:

        line = process.stderr.readline()
        if line:
            print(line.strip())

        if process.poll() is not None:
            break


if __name__ == "__main__":
    """
    Master script to boot either the server or optimiser or both
    """
    parser = argparse.ArgumentParser(description='Boot the TSO servers')
    parser.add_argument('username', type=str,
                        help='The username used for the Tesla API')
    parser.add_argument('--server', action='store_true',
                        help='Boot the monitoring web server')
    parser.add_argument('--optimiser', action='store_true',
                        help='Boot the optimiser controller')
    parser.add_argument('--comm-type', type=str,
                        help='The type of communication between processors LOCAL, DATASTORE, CLOUD_STORAGE')
    args = parser.parse_args()

    if not args.server and not args.optimiser:
        print("You must run the --optimiser or the --server or both.")
        exit(-1)

    # Boot each process in a new thread, so we can print all output from all processes to this console
    threads = []
    if args.optimiser:
        thread_1 = threading.Thread(target=run_process, args=(['python', 'optimiser.py', args.username],))
        thread_1.start()
        threads.append(thread_1)
    if args.server:
        thread_2 = threading.Thread(target=run_process, args=(['python', 'server.py'],))
        thread_2.start()
        threads.append(thread_2)

    for thread in threads:
        thread.join()

    print("Exiting...")

