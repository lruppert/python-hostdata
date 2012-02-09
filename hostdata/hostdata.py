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
    primary_hostname = None # hostname, if any, registered to the host.
    ipv4addr = None # Primary IP address
    ipv6addr = None # Primary IPV6 address
    hwaddr = None # Hardware address for the host.
    user = None # Netid of user associated with this host.
    admin = None # The responsible netid or email for the machine.
    location = None # This might be useful for identifying off-site systems.
    address_class = None # static, dynamic, ???
    secondary_hostnames = [] # These are useful for servers.
    last_seen = None # Good to know whether it is still active.
    description = None # Probably never use this, but it's good to have anyway.
    quarantineable = True # False if a network is noquarantine or static IP
    info = dict()
    
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
# Splunk VPN lookup.  Not accurate.  Needs work on refining timings and lookup
#
## def vpnsearch (ip,eventTime):
    ## print "WARNING: VPN lookups are not yet trusted."
    ## netid = "unknown"
    ## earlyTime = eventTime-timedelta(hours=SEARCHRANGE)
    
    ## spconfig = ConfigParser.ConfigParser()
    ## spconfig.readfp(open("/usr/local/etc/splunk.cfg"))
    ## (host,port) = spconfig.get("Splunk","url").split("/")[2].split(":")
    ## username = spconfig.get("Splunk","user")
    ## pw = spconfig.get("Splunk","password")
    ## p=splunky.Server(host=host, username=username, password=pw)
    
    ## searchQuery = 'host=audit-03 '+ip+' earliest='+earlyTime.strftime("%m/%d/%Y:%H:%M:%S")+' latest='+eventTime.strftime("%m/%d/%Y:%H:%M:%S")+' | head 1'
    ## for r in p.search_sync(searchQuery):
        ## results = str(r['_raw'])
    
    ## rs = re.search('AD\\\\([\w\-]+),',results)
    ## if rs != None :
        ## rnetid = rs.group(1)
        ## if (rnetid != None) :
            ## netid = rnetid
    ## return netid

#
# This replicates the non-printed stuff from the old 'lookup' command.
# It takes a host and a timestamp and then returns a populated host object
class HostLookup :
    
    methods = dict()
    
    def __init__ (self):
        self.pm = PluginManager.PluginManager(config)
        ## Subnet-specific values
        self.hrconfig = csv.reader(open("/etc/hostdata/hostlookup.tab","r"), delimiter='\t')

        # This method of storing it is nowhere near efficient
        for (section,cidr,module) in self.hrconfig:
            self.methods[section,cidr] = module

        
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
        
    def get_hwaddr (self,host,eventTime):
        if (host.ipv6addr):
            mlist = self.get_lookup_method("MAC",host.ipv6addr)
        elif (host.ipv4addr):
            mlist = self.get_lookup_method("MAC",host.ipv4addr)
            
        for dmod in mlist:
            mac_instance = self.pm.get_instance(dmod)
            mac = mac_instance.get_hwaddr(host,eventTime)
            if mac != None:
                return mac
        return None
    
    def get_user(self,host,eventTime):
        if (host.ipv6addr):
            mlist = self.get_lookup_method("user",host.ipv6addr)
        elif (host.ipv4addr):
            mlist = self.get_lookup_method("user",host.ipv4addr)
            
        for dmod in mlist:
            d_inst = self.pm.get_instance(dmod)
            user = d_inst.get_user(host,eventTime)
            if user != None:
                return user
        return None
    
    def get_admin(self,host,eventTime):
        if (host.ipv6addr):
            mlist = self.get_lookup_method("admin",host.ipv6addr)
        elif (host.ipv4addr):
            mlist = self.get_lookup_method("admin",host.ipv4addr)
            
        for dmod in mlist:
            d_inst = self.pm.get_instance(dmod)
            admin = d_inst.get_admin(host,eventTime)
            if admin != None:
                return admin
        return None
    
    # Looks up the basics, like MAC, netid, etc
    def lookup (self,ip,eventTime) :
        resultHost = Host()
        ## We should switch this based on which family and not just assume v4
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
