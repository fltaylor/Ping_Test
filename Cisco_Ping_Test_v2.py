# $language = "python"
# $interface = "1.0"

# CiscoPingTests_v2.py
#
# Cisco Ping Pattern Tests Version 2.0
# This script is built to take a given IPv4 address and run ping pattern tests.
# It will prompt the user for the IP address to ping as well as the interface to
# send pings from.
# Once the user supplies  input, it will run a 1000 count, 1500 byte ping with 
# beginning with data pattern 0x0000.
#

# Setting up for logging
import os


LOG_DIRECTORY = os.path.join(
		os.path.expanduser('~/Downloads/'), 'Ping_Test_Results')

#LOG_FILE_TEMPLATE = os.path.join(
#		LOG_DIRECTORY, iptarget + ".log")

# Define patterns to test with.
PATTERNS = [
			"0x0000", # All zeros
			"0xFFFF", # All ones
			"0x5555", # Alternating ones and zeros
			"0x1111", # One after every 8 bits (tests B8ZS vs AMI)
			"0x1000", # One with 15 zeros
			"0x8080", # One with 7 zeros
			"0x4242", # One followed by 4 consecutive zeros (2 in 8)
			]
# Implement a counter that will increment as data patterns are run.
PATTERNCNT = 0

def Main():
		
	# If the session is not started, warn the user.
	if crt.Session.Connected == False:
		acknowledge = crt.Dialog.MessageBox("Session must be connected for this script to operate properly", "Session Not Connected", ICON_WARN | BUTTON_OK)
		if acknowledge == IDOK:
				return
	
	# Enable synchronous mode to avoid missed output while doing
	# Send/WaitForString sequences
	crt.Screen.Synchronous = True
	
	# Get the current host name so that the program can tell when it is safe to run
	# the next pattern set.
	hostname = crt.Screen.Get(crt.Screen.CurrentRow, 1, crt.Screen.CurrentRow, 25)
	
	# Prompt user for IP address and interface ID
	iptarget = crt.Dialog.Prompt("Enter IP address to test:  ", "IP Address", "", False)
	# If user enters a blank IP address, terminate the script
	if iptarget == "": return
	inttarget = crt.Dialog.Prompt("Enter interface to test from, using the full interface name without spaces (E.G. Serial0/1):  ", "Interface Name", "", False)
	
	# Set up logfile directory
	if not os.path.exists(LOG_DIRECTORY):
		os.mkdir(LOG_DIRECTORY)
	
	if not os.path.isdir(LOG_DIRECTORY):
		crt.Dialog.MessageBox("Log output directory %r is not a directory" % LOG_DIRECTORY)
	
	# Turn on logging to save script output
	crt.Session.LogFileName = LOG_DIRECTORY(iptarget + ".log")
	crt.Session.Log(True)
	
	for PATTERNCNT in range(1,7):
		PingTest()
		PATTERNCNT += 1
		
		
	# Turn Synchronous mode off once script is complete.
	crt.Screen.Synchronous = False
		
Main()

def PingTest():

    # Set the number of times to ping the target.  For the first pass, we want a lower number to ensure that the target is responding
    repcnt = 1000
    if (PATTERNCNT == 0):
        repcnt = 10
        return
       
	# Pattern testing
	crt.Screen.Send("ping" + chr(13))
	crt.Screen.WaitForString("Protocol [ip]: ")
	crt.Screen.Send(chr(13))
	crt.Screen.WaitForString("Target IP address: ")
	crt.Screen.Send(iptarget + chr(13))
	# Error handling for a bad IP address.
	iperror = crt.Screen.WaitForStrings(["Repeat count [5]: ", "% Bad IP address"], 10)
	if (iperror == 2):
		crt.Dialog.MessageBox("Bad IP Address!")
		return
	if (iperror == 0):
		crt.Dialog.MessageBox("Timed Out!")
		return
	crt.Screen.Send(repcnt + chr(13))
	crt.Screen.WaitForString("Datagram size [100]: ")
	crt.Screen.Send(repcnt + chr(13))
	crt.Screen.WaitForString("Timeout in seconds [2]: ")
	crt.Screen.Send("1" + chr(13))
	crt.Screen.WaitForString("Extended commands [n]: ")
	crt.Screen.Send("y" + chr(13))
	crt.Screen.WaitForString("Source address or interface: ")	
	crt.Screen.Send(inttarget + chr(13))
	# Error handling for bad interface names.
	interror = crt.Screen.WaitForStrings(["Type of service [0]: ", "% Invalid source. Must use same-VRF IP address or full interface name without spaces (e.g. Serial0/1)"], 10)
	if (interror == 2):
		crt.Dialog.MessageBox("Invalid source interface.  Must use same-VRF IP address or full interface name without spaces (e.g. Serial0/1).")
		crt.Screen.Send(chr(13))
		crt.Screen.Send(chr(13))
		crt.Screen.Send(chr(13))
		crt.Screen.Send(chr(13))
		crt.Screen.Send(chr(13))
		crt.Screen.Send(chr(13))
		crt.Screen.Send(chr(13))
		break
	if (interror == 0):
		crt.Dialog.MessageBox("Timed Out!")
		return
	crt.Screen.Send(chr(13))
	crt.Screen.WaitForString("Set DF bit in IP header? [no]: ")
	crt.Screen.Send(chr(13))
	crt.Screen.WaitForString("Validate reply data? [no]: ")
	crt.Screen.Send(chr(13))
	crt.Screen.WaitForString("Data pattern [0xABCD]: ")
	crt.Screen.Send(PATTERN[PATTERNCNT] + chr(13))
	crt.Screen.WaitForString("Loose, Strict, Record, Timestamp, Verbose[none]: ")
	crt.Screen.Send(chr(13))
	crt.Screen.WaitForString("Sweep range of sizes [n]: ")
	crt.Screen.Send(chr(13))
	
PingTest()