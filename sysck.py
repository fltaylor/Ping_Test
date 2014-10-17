# $language = "python"
# $interface = "1.0"

import platform

def sysck():
    """Script to determin various properties of SecureCRT and
    the host you are connected to."""
    
    localhost = crt.Session.LocalAddress
    remotehost = crt.Session.RemoteAddress
    pyver = platform.python_version()
    
    crt.Dialog.MessageBox('Local host = %r \nRemote Host = %r \nPython version = %r' % (localhost, remotehost, pyver))
                          
sysck()
