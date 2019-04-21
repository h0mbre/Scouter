

# Scouter

Scouter is used to automate a typical initial port-scanning workflow, particularly on hackthebox.eu. The script enumerates:
1. default TCP ports (1000 ports)
2. non-default TCP ports (the other ~64500 ports)
3. the top 500 UDP ports (or top 100 slowly if the 'slow' flag is set)

**Please keep in mind that it was tested specifically for the hackthebox VPN environment.**

USAGE: 

`scouter.py 10.10.10.10 [OPTIONAL:outputformat] [OPTIONAL:interface] [OPTIONAL:UDP scan options]`

`scouter.py 10.10.10.10`

`scouter.py 10.10.10.10 -oN -i tun0 -s`

`scouter.py 10.10.10.10 -oN --interface tun0 --slow`

OUTPUT:

`-oA: save output in the nmap three major formats at once`

`-oN: save output in the nmap normal format`

`-oX: save output in the nmap XML format`

`-oS: save output in the nmap s|<rIpt kIddi3 format`

`-oG: save output in the nmap Grepable format`

INTERFACE:

`-i, --interface: select an interface for masscan to scan against, default is tun0`

UDP SCAN OPTIONS:

`-s, --slow: enable slower UDP scan against the top 100 UDP ports, default is no rate limit scan of UDP top 500`

Detailed Workflow:
1. Runs a standard `nmap -sC -sV <target IP>` scan for default TCP ports
2. Looks for non-default TCP ports with `masscan -p(list of non-default nmap ports) --rate=1000 -e tun0 <target IP>` and `nmap -p(list of non-default nmap ports) <target IP>` and takes the output of whichever finishes first
3. If there are any results outside of the default nmap port range, the script will run a follow-up `nmap -sC -sV` scan on those ports
4. Runs a top 500 ports `nmap -sU --top-ports 500 --defeat-icmp-ratelimit <target IP>` scan by default
5. If there are any UDP ports discovered, the script will run a follow-up `nmap -sU -sC -sV` scan on those ports
6. If the slow flag is enabled, it will run a slower `nmap -sU --top-ports 100` scan and follow up on any open ports. 

Add this entry to your .bashrc file: `alias scouter='python /root/filepath/scouter.py'` and you can just call the script with 'scouter <i<ip>p>.'

### Thanks 
To dirsearch for color scheme inspiration (I just shamelessly ripped it off!) 

To Daniel Miller (@bonsaiviking)

HMU on twitter @h0mbre_ if you get anything out of it! 




