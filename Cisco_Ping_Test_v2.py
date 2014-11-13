# $language = "python"
# $interface = "1.0"

# CiscoPingTests_v2.0.py
#
# Cisco Ping Pattern Tests Version 2.0
# This script is designed to be used on Cisco devices while using the SecureCRT
# SSH/Telnet client (http://www.vandyke.com/products/securecrt/).
# In order for this script to properly execute, the user must be in exec/enable
# mode.
# It will prompt the user for an IPv4 address to ping as well as any interfaces
# to capture statistics from in the logs.  Once the user supplies input, it will
# run a 1000 count, 1500 byte ping with beginning with data pattern 0x0000.
#
# Built 02 NOV 2014
# Forrest L. Taylor

import os
import datetime

# Declaring global variables
IPTARGET = ""
INTTARGET = []
HOSTNAME = ""
# Implement a counter that will increment as data patterns are run.
PATTERNCNT = 0
# Define patterns to test with.
PATTERNS = [
    '0xABCD', # Standard data pattern, will be used for response verification
    '0x0000', # All zeros
    '0xFFFF', # All ones
    '0x5555', # Alternating ones and zeros
    '0x1111', # One after every 8 bits (tests B8ZS vs AMI)
    '0x1000', # One with 15 zeros
    '0x8080', # One with 7 zeros
    '0x4242', # One followed by 4 consecutive zeros (2 in 8)
    ]

def main():

    global IPTARGET
    global INTTARGET
    global PATTERNCNT
    global PATTERNS
    global HOSTNAME

    # If the session is not started, warn the user.
    if crt.Session.Connected == False:
        acknowledge = crt.Dialog.MessageBox('Session must be connected for this script to operate properly',
                                            'Session Not Connected', ICON_WARN | BUTTON_OK)
        if acknowledge == IDOK:
            return

    # Verify that logging is off, and if it is on, turn it off.
    if crt.Session.Logging == True:
        crt.Session.Log(False)

    # Enable synchronous mode to avoid missed output while doing
    # Send/WaitForString sequences
    crt.Screen.Synchronous = True

    # Get the current host name so that the program can
    # tell when it is safe to run the next pattern set.
    rowindex = crt.Screen.CurrentRow
    colindex = crt.Screen.CurrentColumn - 1
    HOSTNAME = crt.Screen.Get(rowindex, 0, rowindex, colindex)
    HOSTNAME = HOSTNAME.strip()

    # Prompt user for IP address and interface ID
    IPTARGET = crt.Dialog.Prompt('Enter IP address to test:  ',
                                 'IP Address', '', False)
    # If user enters a blank IP address, terminate the script
    if IPTARGET == '':
        quit()
    # Have the user determine if they want to capture the statistics for a
    # certain interface.
    getints = crt.Dialog.MessageBox('Are there any associated interfaces to capture statistics from? \nWARNING:  Choosing this option will clear interface statistics!',
                                       'Interface Association', ICON_QUESTION | BUTTON_YESNO | DEFBUTTON2)
    if getints == IDYES:
        interfaceget(INTTARGET)

    logging(IPTARGET)
    clearstats()  # Clearing stats prior to running for better visibility.
    for PATTERNCNT in range(0, 8):
        if PATTERNCNT != 0:
            append()
        pingtest()
        if len(INTTARGET) != 0:
            statscapture()
            clearstats()

    # Turn Synchronous mode off once script is complete.
    crt.Screen.Synchronous = False


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def pingtest():
    """Verifies IP target is responding and runs patterns against the target"""
    global IPTARGET
    global INTTARGET
    global PATTERNCNT
    global PATTERNS
    global HOSTNAME

    # Turn on logging to capture and append test output to current log
    crt.Session.Log(True, True)
    # Set the number of times to ping the target.  For the first pass, we want
    # a lower number to ensure that the target is responding.
    repcnt = '1000'
    pktsize = '1500'
    if PATTERNCNT == 0:
        repcnt = '10'
        pktsize = '100'

    # Pattern testing
    crt.Screen.Send('ping' + chr(13))
    crt.Screen.WaitForString('Protocol [ip]: ')
    crt.Screen.Send(chr(13))
    crt.Screen.WaitForString('Target IP address: ')
    crt.Screen.Send(IPTARGET)
    crt.Screen.Send(chr(13))
    # Error handling for a bad IP address.
    iperror = crt.Screen.WaitForStrings(['Repeat count [5]: ',
                                         '% Bad IP address'], 10)
    if iperror == 2:
        crt.Dialog.MessageBox('Bad IP Address!')
        quit()
    if iperror == 0:
        crt.Dialog.MessageBox('Timed Out!')
        quit()
    crt.Screen.Send(repcnt)
    crt.Screen.Send(chr(13))
    crt.Screen.WaitForString('Datagram size [100]: ')
    crt.Screen.Send(pktsize + chr(13))
    crt.Screen.WaitForString('Timeout in seconds [2]: ')
    crt.Screen.Send('1' + chr(13))
    crt.Screen.WaitForString('Extended commands [n]: ')
    crt.Screen.Send('y' + chr(13))
    crt.Screen.WaitForString('Source address or interface: ')
    crt.Screen.Send(chr(13))
    crt.Screen.WaitForString('Type of service [0]: ')
    crt.Screen.Send(chr(13))
    crt.Screen.WaitForString('Set DF bit in IP header? [no]: ')
    crt.Screen.Send(chr(13))
    crt.Screen.WaitForString('Validate reply data? [no]: ')
    crt.Screen.Send(chr(13))
    crt.Screen.WaitForString('Data pattern [0xABCD]: ')
    crt.Screen.Send(PATTERNS[PATTERNCNT] + chr(13))
    crt.Screen.WaitForString('Loose, Strict, Record, Timestamp, Verbose[none]: ')
    crt.Screen.Send(chr(13))
    crt.Screen.WaitForString('Sweep range of sizes [n]: ')
    crt.Screen.Send(chr(13))

    # Ensure that target is responding, and if not, terminate the script.
    if PATTERNCNT == 0:
        if crt.Screen.WaitForString('Success rate is 0 percent (0/10)', 10) == True:
            crt.Dialog.MessageBox('Target is not responding.  Terminating script.')
            quit()
        else:
            cursorpause()

    cursorpause()
    # Turn off logging to allow for other input before moving on.
    crt.Session.Log(False)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def logging(target):
    """Sets up logging to capture test output"""

    log_directory = os.path.join(os.path.expanduser('~'), 'Downloads')
    # Set up logfile directory
    if not os.path.exists(log_directory):
        os.mkdir(log_directory)

    if not os.path.isdir(log_directory):
        crt.Dialog.MessageBox('Log output directory %r is not a directory' 
                              % log_directory)

    # Set up the log file
    log_filename = (target + ".log")
    log_file_template = os.path.join(log_directory, log_filename)
    crt.Session.LogFileName = (log_file_template)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def cursorpause():
    '''Waits for cursor to pause before continuing.'''
    while True:
        cursor = crt.Screen.WaitForCursor(1)
        if cursor == False:
            break
    # Once the cursor has stopped moving for about a second, we'll
    # assume it's safe to start interacting with the remote system.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def statscapture():
    '''Capture interface stats after pattern completion.'''
    #This whole method needs to be re-written to support the new format.
    intcount = 0
    # Turn on logging to capture and append test output to current log.
    crt.Session.Log(True, True)
    # Send a show interface command for the appropriate interface.
    for intcount in range(0, len(INTTARGET)):
        crt.Screen.Send("show interface " + INTTARGET[intcount])
        crt.Screen.Send(chr(13))
        while True:
            if crt.Screen.WaitForString(' --More-- ', 2) == True:
                crt.Screen.Send(' ')
            else:
                crt.Session.Log(False)
                return

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def clearstats():
    '''Clears the interface statistics of target interfaces.'''
    #Ensures logging is off.  No need to capture this output.
    crt.Session.Log(False)
    intcount = 0
    for intcount in range(0, len(INTTARGET)):
        crt.Screen.Send("clear counters " + INTTARGET[intcount])
        crt.Screen.Send(chr(13))
        crt.Screen.WaitForString('Clear "show interface" counters on this interface [confirm]')
        crt.Screen.Send(chr(13))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def append():
    '''Appends log with date/time, current pattern to run, and clears
    counters on interfaces'''
    now = str(datetime.datetime.now())
    curpattern = PATTERNS[PATTERNCNT]
    # Ensure logging is off
    crt.Session.Log(False)
    textToAdd = ('\n/********************************************/ \n/* ' + now + ': \n/* Target:  '
    + IPTARGET + '\n/* Current Pattern:  ' + curpattern
    + '\n/*******************************************/ \n')

    WriteToFile(crt.Session.LogFileName, textToAdd)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def interfaceget(INTTARGET):
    '''Gets associated interfaces to capture'''
    interface = crt.Dialog.Prompt('Input target interface (I.E. Serial7/0/1/18:1):  ',
                                  'Enter Interface', '', False)
    if interface == '':
        return
    else:
        INTTARGET.append(interface)
        while True:
            if crt.Dialog.MessageBox('Enter another interface target?',
                                     'More interfaces?', ICON_QUESTION | BUTTON_YESNO | DEFBUTTON2) == IDYES:
                interface = crt.Dialog.Prompt('Input target interface (I.E. Serial1/0/7:0):  ', 'Enter Interface', '', False)
                if interface == '':
                    break
                else:
                    INTTARGET.append(interface)
            else:
                break

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def WriteToFile(filename, data):
	# filename: Full path to file
	# data: data to be written to the logfile
	f = file(filename, 'a')
	f.write(data)
	f.close()
    
    


main()
