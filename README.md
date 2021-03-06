>Whoever conceals their syns does not prosper..<br/>

*-Proverbs 28:13*
# The Godspeed Project
2 Python port scanners I created to help speed up certain CTF tasks, but mostly just for fun.<br/>

Like many other homemade port scanners, the goal was to quickly identify all open ports, which could then be taken to nmap for further enumeration. The puposes being efficient time management(speed), and identifying services running on any of the non-standard ports nmap doesn't check by default.</br>
Their functional speed is mostly dependant on network connection, and various target/scanner/host configurations. (More on that below)<br/>
Neither of them were designed to be subtle (see quote), and are obviously not meant for "professional" use.<br/>

godspeed.py - Multi-threaded TCP Connect scanner<br/>
originalSYN.py - Single-threaded TCP SYN scanner<br/>

***As of godspeed v1.1.1, the fastest average is 7.41 seconds for all 65,535 ports. (n=10)<br/>***

*Developed using python3.9, but it should work with any recent python3. I purposely used only built-ins and avoided newer modules/functions*
## godspeed.py
A multi-threaded TCP Connect scanner, targeting all 65,535 ports. Along with open ports, it outputs an nmap-friendly command for an easy transition between the two. Overall, it's pretty simple. Half the filesize is argument parsing code.<br/>

Scan time is typically less than 8 seconds. If it's more than 15, consider increasing the thread count.
### Usage
Accepts a target IP via the command line, along with a few optional flags to increase optimization for specific targets. The default thread count is 100, which I found was most optimal for virtual machines on my local network. The slower the network speed, the more efficient increasing the thread count is, generally.
```
godspeed.py [options] target_ip

positional arguments:
  target_ip                      IP address to scan

optional arguments:
  -h, --help                     show this help message and exit
  -q, --quiet                    Output nothing but the nmap command
  -w THREADS, --threads THREADS  Amount of working threads to run. (Default=100)
  -t TIMEOUT, --timeout TIMEOUT  Connection timeout, in seconds. (Default=0.3)

Examples:
godspeed.py 192.168.1.1
godspeed.py --threads=400 -q 10.10.10.23
godspeed.py -w 150 --timeout 1.2 192.168.1.50
```
**Output**
```
$ ./godspeed.py 192.168.1.50
Port 9090 open
Port 10119 open
Port 12654 open
Port 13000 open

Scan completed at 7.64637s
4 open TCP port(s) found.

suggested nmap command:
nmap -p 9090,10119,12654,13000 -sV -Pn -sC -T4 192.168.1.50
```
### Notes and Issues
- Some machines won't respond to requests to closed ports, which leads to godspeed relying on the connection timeout to determine if it's closed. This absolutely tanks the scan time.
  - This can be mitigated by increasing with thread count with ***-w*** or ***--threads*** and/or decreasing the timeout with ***-t*** or ***--timeout***.
- A timeout of .3 can occasionally lead to missing RST packets and identifying a port as "unresponsive"
  - This is pretty rare (~5/65535) but it could potentially lead to false negatives.

## originalSYN.py
A (single-threaded) TCP SYN scanner, capable of targeting one or more specific ports. It generates its own TCP headers and delivers them via raw sockets.<br/> 
The Godspeed Project itself was originally meant to just be a SYN scanner, but that was annoying to impliment with threading, and processing a few extra TCP Handshake packets ultimately has little/no effect on the scan speed unless a VERY significant amount of ports are open. OriginalSYN remains mostly a proof of concept, but I found it useful for quickly testing individual ports/ranges to observe their behavior in wireshark, or confirming their open/closed/unresponsive status.<br/>

Scan time is generally ~7000 ports per second, under normal conditions, with full port scans taking ~10 seconds.
### Usage
Accepts a target IP and ports via command line, along with optional flags. The default timeout is higher than godspeed's, since it's typically used it to identify whether a port is unresponsive or just slow, but it can lowered to increase speed.<br/> 

Ports can be submitted individually, as a range (1-3), or any combination of the two (1-3 4 5 6-9).
```
originalSYN.py [options] target_ip ports

positional arguments:
  target_ip                      IP address to scan
  ports                          Port, ports, or port range to scan

optional arguments:
  -h, --help                     show this help message and exit
  -v, --verbose                  Output closed/irregular responses, and non-responsive ports
  -t TIMEOUT, --timeout TIMEOUT  Connection timeout, in seconds. (Default=0.5)

Examples:
originalSYN.py 192.168.1.1 8080
originalSYN.py -v -t 15 10.10.10.23 9090 9091 9092-9095 38650
originalSYN.py --timeout=.1 192.168.1.50 1-65535
```
**Output**
```
$ sudo ./originalSYN.py -v 192.168.1.45 80 443 9090-9093
Port 80 is open
Port 443 is closed
Port 9090 is open
Port 9091 is open
Port 9092 is closed
Port 9093 is open
6 port(s) scanned, 4 found open.
Completed in 0.002007741015404463s
```
### Notes and Issues
- 2/3rds of the filesize is overly comprehensive argument parsing and error handling code
- Requires sudo/root privileges, due to raw socket usage
- Currently only works on linux, because windows does not allow you to use raw sockets for TCP. 
## To do
- Add UDP functionality (ogSYN, probably)
- Make threading code less hideous/more efficient (godspeed)
- Add more religious iconography
## Disclaimer
*(In case any one actually finds their way here)*<br/>
While port scanning hosts/servers without permission isn't technically a crime in the US, the owners of said hosts/servers absolutely do not like it. Ramifications of an unauthorized scan may include (but are not limited to) IP banishment, lawsuits, and/or losing your internet by violating your ISP's Acceptable Use Policy.
