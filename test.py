# Testing implmentation options for running through patterns.

PATTERN = ["0x0000", "0xFFFF", "0xABCD", "0x1111"]
PATTERNCNT = 0

def Printy():
    
    global PATTERN
    global PATTERNCNT    
    repcnt = 1000    
    
    if (PATTERNCNT == 0):
        repcnt = 5

    print PATTERN[PATTERNCNT]
    print "some stuff here"
    print "more stuff here"
    print PATTERNCNT
    print repcnt
    
Printy()

def Main():
    
    global PATTERN
    global PATTERNCNT
    
    for PATTERNCNT in range(1, 4):
        Printy()
        PATTERNCNT += 1
    print "All done!"
        
Main()