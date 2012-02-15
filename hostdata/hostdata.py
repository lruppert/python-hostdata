# Copyright Lou Ruppert
import ConfigParser
import ipcalc
import re
import csv
from datetime import timedelta
# And our own components
import PluginManager

## Behavior and app-wide defaults
config = ConfigParser.ConfigParser()
config.readfp(open("/etc/hostdata/hostdata.cfg"))

class Host :
    hostname = None # Primary hostname, if any, registered to the host.
    ipv4addr = None # Primary IP address
    ipv6addr = None # Primary IPV6 address
    hwaddr = None # Hardware address for the host.
    user = dict() # Collection of data for the user
    admin = dict() # Collection of admin contact data for the machine.
    address_class = None # DHCP-static, DHCP-dynamic, VPN, ???
    info = dict() # Miscellaneous site-only fields
    raw = dict() # A dictionary of dictionaries for storing raw db data from queries
    
    def getInfo(self,key):
        if key in self.info:
            return self.info[key]
        else:
            return None

    def setInfo(self,key,value):
        self.info[key] = value

    def isDynamic(self):
        if (self.address_class != "hardcoded"):
            return True
        else:
            return False



#
# This replicates the non-printed stuff from the old 'lookup' command.
# It takes a host and a timestamp and then returns a populated host object
class HostLookup :
    hrconfig = None
    methods = dict()
    
    def __init__ (self,hlconfig=None,hrconfig=None):
        self.pm = PluginManager.LookupPluginManager(config)
        ## Subnet-specific values
        self.hrconfig = csv.reader(open("/etc/hostdata/hostlookup.tab","r"), delimiter='\t')

        # This method of storing it is nowhere near efficient
        for (section,cidr,module) in self.hrconfig:
            self.methods[section,cidr] = module

    # This returns a list containing the chain of lookups configured for the attribute and subnet
    def get_lookup_method(self,section,ip):
        mlist = None
        for (hsection,cidr) in self.methods:
            if (section == hsection and ip in ipcalc.Network(cidr)):
                mstring = self.methods[hsection,cidr]
                mlist = mstring.split(",")
                if mlist:
                    return mlist
        # If after traversing the whole structure we still have nothing,
        # we give it a set of dummy values so that the methods don't fail
        if not mlist:
            mlist = ["Dummy",]
        return mlist
        
    # This walks the chain, finally setting the host attribute and returning it
    def get_hwaddr (self,host,eventTime):
        if (host.ipv6addr):
            mlist = self.get_lookup_method("MAC",host.ipv6addr)
        elif (host.ipv4addr):
            mlist = self.get_lookup_method("MAC",host.ipv4addr)
            
        for dmod in mlist:
            mac = None
            mac_instance = self.pm.get_instance(dmod)
            macdict = mac_instance.get_hwaddr(host,eventTime)
            if ("hwaddr" in macdict.keys()):
                mac = macdict["hwaddr"]
            if mac != None:
                return mac
        return None
    
    # This walks the chain, finally setting the user attributes and returning them
    def get_user(self,host,eventTime):
        user = None
        if (host.ipv6addr):
            mlist = self.get_lookup_method("user",host.ipv6addr)
        elif (host.ipv4addr):
            mlist = self.get_lookup_method("user",host.ipv4addr)
            
        for dmod in mlist:
            d_inst = self.pm.get_instance(dmod)
            userdict = d_inst.get_user(host,eventTime)
            if ("user" in userdict.keys()):
                user = userdict["user"]
            if user != None:
                return user
        return None
    
    # This walks the chain, finally setting the admin attributes and returning them
    def get_admin(self,host,eventTime):
        admin = None
        if (host.ipv6addr):
            mlist = self.get_lookup_method("admin",host.ipv6addr)
        elif (host.ipv4addr):
            mlist = self.get_lookup_method("admin",host.ipv4addr)
            
        for dmod in mlist:
            d_inst = self.pm.get_instance(dmod)
            admindict = d_inst.get_admin(host,eventTime)
            if ("admin" in admindict.keys()):
                admin = admindict["admin"]
            if admin != None:
                return admin
        return None
    
    # Looks up the basics, like MAC, netid, etc
    # Legacy.
    def lookup (self,ip,eventTime) :
        resultHost = Host()

        if (ip in ipcalc.Network("0.0.0.0/0")):
            resultHost.ipv4addr = ip
        elif (ip in ipcalc.Network("0::/0")):
            resultHost.ipv6addr = ip
        else:
            print "ERROR: No recognized IP format for %s" % ip
            resultHost.ipv4addr = ip
    
        resultHost.hwaddr = self.get_hwaddr(resultHost,eventTime)
        resultHost.user = self.get_user(resultHost,eventTime)
        resultHost.admin = self.get_admin(resultHost,eventTime)
        return resultHost
