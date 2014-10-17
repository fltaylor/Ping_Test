# Testing implmentation options for running through patterns.

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
PATTERNCNT = 0
IPTGT = "null"

def Main():
    
    global PATTERNS
    global PATTERNCNT
    global IPTGT
    
    IPTGT = raw_input("Input IP address:  ")
    if IPTGT == "":
        quit()
    print IPTGT
    
    for PATTERNCNT in range(0, 8):
        Printy()
        
    print "All done!"
        
def Printy():
    
    global PATTERNS
    global PATTERNCNT    
    global IPTGT
    repcnt = 5    
    
    if (PATTERNCNT > 0):
        repcnt = 1000

    print "\n"
    print PATTERNS[PATTERNCNT]
    print "some stuff here"
    print "more stuff here"
    print PATTERNCNT
    print repcnt
    print IPTGT
    PATTERNCNT += 1
    
Main()