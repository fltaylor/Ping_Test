# $language = "python"
# $interface = "1.0"

# CiscoPingTests_v1.py
#
# Cisco Ping Pattern Tests Version 1.0
# This script is designed to be used on Cisco devices while using the SecureCRT
# SSH/Telnet client (http://www.vandyke.com/products/securecrt/).
# In order for this script to properly execute, the user must be in exec/enable
# mode.
# It will prompt the user for an IPv4 address to ping as well as the interface
# to send pings from.  Once the user supplies input, it will run a 1000 count, 
# 1500 byte ping with beginning with data pattern 0x0000.
#


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
IPTARGET = ""
INTTARGET = ""
# Implement a counter that will increment as data patterns are run.
PATTERNCNT = 0

def main():

    global IPTARGET
    global INTTARGET
    global PATTERNCNT
    global PATTERNS

    # If the session is not started, warn the user.
    if crt.Session.Connected == False:
        acknowledge = crt.Dialog.MessageBox('Session must be connected for this script to operate properly', 'Session Not Connected', ICON_WARN | BUTTON_OK)
        if acknowledge == IDOK:
            return

    # Enable synchronous mode to avoid missed output while doing
    # Send/WaitForString sequences
    crt.Screen.Synchronous = True

    # Prompt user for IP address and interface ID
    IPTARGET = crt.Dialog.Prompt('Enter IP address to test:  ',
                                 'IP Address', '', False)
    # If user enters a blank IP address, terminate the script
    if IPTARGET == '':
        quit()
    INTTARGET = crt.Dialog.Prompt('Enter interface to test from, using the full interface name without spaces (E.G. Serial1/0/7:0):  ', 'Interface Name', '', False)

    for PATTERNCNT in range(0, 7):
        pingtest()



    # Turn Synchronous mode off once script is complete.
    crt.Screen.Synchronous = False


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def pingtest():
    """Verifies IP target is responding and runs patterns against the target"""
    global IPTARGET
    global INTTARGET
    global PATTERNCNT
    global PATTERNS

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
    crt.Screen.Send(INTTARGET + chr(13))
    # Error handling for bad interface names.
    interror = crt.Screen.WaitForStrings(['Type of service [0]: ', '% Invalid source. Must use same-VRF IP address or full interface name without spaces (e.g. Serial0/1)'], 10)
    if interror == 2:
        crt.Dialog.MessageBox('Invalid source interface.  Must use same-VRF IP address or full interface name without spaces (e.g. Serial0/1).')
        quit()
    if interror == 0:
        crt.Dialog.MessageBox('Timed Out!')
        quit()
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
        if crt.Screen.WaitForString('Success rate is 0 percent (0/10)', 12) == True:
            crt.Dialog.MessageBox('Target is not responding.  Terminating script.')
            quit()

main()
