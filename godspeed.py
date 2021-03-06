#!/usr/bin/python3

"""
godspeed.py by LLCZ00

Look! He advances like the clouds,
   his chariots come like a whirlwind,
his horses are swifter than eagles.
   Woe to us! We are ruined!
- Jeremiah 4:13
"""
_v='v1.1.2'

import socket
import sys
import time
import threading
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

lock = threading.Lock()


class LLCZ00Parser(argparse.ArgumentParser): # better error handler
    def error(self, message):
        print("Error. {}".format(message))
        sys.exit("Try '{} --help' for more information".format(self.prog))

def argument_handler():
	parser = LLCZ00Parser(
		prog='godspeed.py',
		usage="%(prog)s [options] target_ip", 
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description="GODSPEED Scanner {}:\nPerforms a relatively quick TCP Connect scan of all 65,535 ports.\nOutputs nmap-friendly command for further enumeration.".format(_v),
		epilog="Examples:\n%(prog)s 192.168.1.1\n%(prog)s --threads=400 -q 10.10.10.23\n%(prog)s -w 150 --timeout 1.2 192.168.1.50"
	)
	parser.add_argument(
		'-q', '--quiet',
		help="Output nothing but the nmap command",
		dest='quiet',
		action='store_true'
	)	
	parser.add_argument(
		'-w', '--threads',
		help="Amount of working threads to run. (Default=%(default)s)",
		default=100,
		dest='threads',
		type=int
	)
	parser.add_argument(
		'-t','--timeout',
		help="Connection timeout, in seconds. (Default=%(default)s)",
		default=0.3,
		dest='timeout',
		type=float,
		metavar='TIMEOUT'	
	)	
	parser.add_argument(
		'target_ip',
		help="IP address to scan"
	)	


	cmd = parser.parse_args()

	# ip validity check
	try:
		packed = socket.inet_aton(cmd.target_ip) 
		if cmd.target_ip != socket.inet_ntoa(packed):
			parser.error("invalid ip: {}".format(cmd.target_ip))
	except OSError:
		parser.error("invalid ip: {}".format(cmd.target_ip))

	return cmd


def connect(dip, port, q):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:	
		try:
			s.connect((dip, port))
			with lock:
				open_ports.append(str(port))
				if not q:
					print("Port {} open".format(port))
		except ConnectionRefusedError:
			pass


if __name__ == '__main__':
	args = argument_handler()

	socket.setdefaulttimeout(args.timeout)
	dst_ip = args.target_ip
	threads = args.threads
	quiet = args.quiet # "quiet mode" flag. default is false

	open_ports = []

	t = time.perf_counter()
	# Threading. May revisit, could be better
	with ThreadPoolExecutor(max_workers=threads) as ex: 
		connections = [ex.submit(connect, dst_ip, port, quiet) for port in range(1,65536)] # compile list of futures
		for _ in as_completed(connections): # run
			pass

	if not quiet:
		print("\nScan completed at {:.5f}s".format(time.perf_counter() - t))
		print("{} open TCP port(s) found.\n".format(len(open_ports)))

	if open_ports != []:
		print("suggested nmap command:")		
		print("nmap -p {} -sV -Pn -sC -T4 {}".format(','.join(open_ports), dst_ip))
	elif quiet:
		print("Quiet Mode: No open ports found.")
		
