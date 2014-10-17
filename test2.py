def Main():
    
# Setting up for logging
import os
import crt

IPTARGET = ""
LOGDIRECTORY = os.path.join(os.path.expanduser('~/Downloads/'))
#LOGFILETEMPLATE = os.path.join(LOGDIRECTORY, IPTARGET + ".log")

def logging():
    
    global IPTARGET
    
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
    INTTARGET = crt.Dialog.Prompt('Enter interface to test from, using the full interface name without spaces (E.G. Serial0/1):  ', 'Interface Name', '', False)

    # Set up logfile directory
    if not os.path.exists(LOGDIRECTORY):
        os.mkdir(LOGDIRECTORY)
	
    if not os.path.isdir(LOGDIRECTORY):

        crt.Dialog.MessageBox('Log output directory %r is not a directory' % LOG_DIRECTORY)
    
    
    # Turn on logging to save script output
    crt.Session.LogFileName = (IPTARGET + '.log')
    #open(LOGFILETEMPLATE, a)
    crt.Session.Log(True)
    print 'Logging set and enabled'
    
logging()

    
Main()