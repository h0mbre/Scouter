# Scouter

Scouter is used to automate a typical initial port-scanning workflow, particularly on hackthebox.eu. The script enumerates:
1. default TCP ports (1000 ports)
2. non-default TCP ports (the other 64000 ports)
3. the top 500 UDP ports (or top 100 slowly if the 'slow' flag is set)

**Please keep in mind that it was tested specifically for the hackthebox VPN environment.**

Usage: 
`scouter.py 10.10.10.10`
`scouter.py 10.10.10.10 -s, --slow` ( 

At a high-level the script does the following:
1. Scans default nmap TCP port range
2. Scans non-default nmap TCP port range
3. Scans UDP port range in accordance with CLI arguments

Detailed Workflow:
1. Takes an IP address + optional 'slow' flag and runs a standard `nmap -sC -sV <target IP>` scan for default TCP ports
2. Looks for non-default TCP ports with a `masscan -p(list of non-default nmap ports) --rate=1000 -e tun0 <target IP>` scan
4. If there are any results outside of the default nmap port range, the script will run a follow-up `nmap -sC -sV` scan on those ports
5. Runs a top 500 ports `nmap -sU --top-ports 500 --defeat-icmp-ratelimit <target IP>` scan by default
6. If there are any UDP ports discovered, the script will run a follow-up `nmap -sU -sC -sV` scan on those ports
7. If the slow flag is enabled, it will run a slower `nmap -sU --top-ports 100` scan and follow up on any open ports. 

Add this entry to your .bashrc file: `alias scouter='python /root/filepath/scouter.py'` and you can just call the script with 'scouter <i<ip>p>.'


## Details and Weird Discoveries

### Background
Scouter is the result of me trying to speed up and automate my hackthebox.eu initial scanning work-flow. I am very new to scripting/writing python code so I thought it would be a good learning opportunity. Some details about what I learned below. 

### Masscan is very naughty! 
Boy does masscan like to bug out over a VPN connection. I found that it regularly misses open UDP ports to the point that I could not rely on it. This problem persisted even if the scanning rate was decreased to 200 packets per second. 

I also found that masscan likes to hang. It will display a counter telling you when it plans on exiting and this counter will plunge into the -300 second range on occasion. I put a function in the script called 'cop' which will run for 2 mins and then kill masscan in case it has hung on us. **Remember to change the hardcoded interface if you wish to scan a non-HTB network.** After some testing,  `nmap -p- <target>` is about twice as fast as `masscan -p1-65535 --rate=1000 -e tun0 <target>` when the nmap scan works correctly, however, this is not always the case. To be careful, I'm still relying on masscan because numerous times I've found that masscan will complete a all ports TCP scan faster than nmap -p- which will run forever in those instances.

###### WTF?
The **weirdest** thing I discovered, was that if you run a UDP all-ports scan with masscan and simultaneously run an `nmap -sU` scan of any sort, the nmap results will be lightning quick. I have had idea why this worked, Daniel Miller on twitter (@bonsaiviking) said it is probably similar to using the `--defeat-icmp-ratelimit -sU` flag. You can find his explanation [here](https://twitter.com/bonsaiviking/status/1109492944598376448). One box I tested took 107 seconds without masscan to scan the nmap -sU top 100, and only took 3 seconds to scan the same range with masscan running concurrently. After some testing, I found that Daniel's --defeat-icmp-ratelimit flag was just as fast as running masscan concurrently. **Keep in mind that defeating the ICMP rate limit can lead to inaccurate results, so if you want to be careful use the slow flag.**

The script could be easily altered to take advantage of a better masscan if used outside of the hackthebox environment. Have fun altering it to suit your needs.

### Hardcoded Bash Commands
I used a lot of hardcoded bash commands in the script so I could learn more about CLI utilities such as awk, cut, sed, head, tr, etc. I'm sure the string slicing methods available in Python could be leveraged to change the output as well, I just preferred to learn some bash-friendly commands. If you're not a fan of the hardcoded commands or the output format, change it up!

### Multi-Processing
The script takes advantage of multi-processing by running a bunch of the commands simultaenously, this greatly reduces the scanning time. My original script, which performed all the commands in a linear fashion finished a test box in ~6 minutes, while this multi-processing version finished the same box in ~2 minutes flat. Maybe this script is better suited for multi-threading? I'm not sure, I did some reading on the topic of I/O-bound vs. CPU-bound programs but was unable to devote much time to it. Let me know if you know the answer and I'll come back to it at some point.

### Argument Parsing
This is the part I'm most ashamed of, the CLI-argument parsing seems very clumsy haha. Feel free to tell me how to do it better. I'm very new to this. 

### Known Bugs
There is an outcome that occurs sometimes where after the script runs, key strokes will not print to the terminal. The terminal can still be killed by entering 'exit,' you just won't be able to see the command as it's being typed.

### Thanks 
To dirsearch for color scheme inspiration (I just shamelessly ripped it off!) 

To Daniel Miller (@bonsaiviking)

HMU on twitter @h0mbre_ if you get anything out of it! 




