# Copyright (C) 2012 Lou Ruppert.  All Rights Reserved
# Author: Lou Ruppert <himself@louruppert.com>
#
# We may need to split this into separate modules for ISC and dnsmasq DHCP
# and for Splunk vs ELSA vs DB storage of records
#
# Splunk lookups use Justin Azoff's 'splunky' module, available on GitHub
#

from hostdata.PluginManager import LookupPlugin
from datetime import timedelta
import ConfigParser,re
import splunky
#
# This class serves as the example as well as a useful endpoint to searches
# or a means of suppressing them.
class DHCPLookup(LookupPlugin):
    def __init__(self):
        
        spconfig = ConfigParser.ConfigParser()
        spconfig.readfp(open("/usr/local/etc/splunk.cfg"))
        (host,port) = spconfig.get("Splunk","url").split("/")[2].split(":")
        username = spconfig.get("Splunk","user")
        pw = spconfig.get("Splunk","password")
        self.splunk_server=splunky.Server(host=host, username=username, password=pw)
        
    def get_hwaddr(self,host,eventtime):
        hwaddr = None
        results = None
        earlyTime = eventtime-timedelta(hours=4)
    
        searchQuery = 'source=/data/syslog/network/dhcp '+host.ipv4addr+' DHCPACK earliest='+earlyTime.strftime("%m/%d/%Y:%H:%M:%S")+' latest='+eventtime.strftime("%m/%d/%Y:%H:%M:%S")+' | head 1'
        for r in self.splunk_server.search_sync(searchQuery):
            results = str(r['_raw'])
        if not results:
            return {}
        m = re.search('\(([01234567890abcdef\:]+)\)',results)
        if (m == None) :
            m = re.search('([01234567890abcdef\:]{17})',results)
        if (m != None) :
            hwaddr = m.group(1)
            hwaddr = hwaddr.translate(None,':')

        return { "hwaddr" : hwaddr }

    # This returns None unless someone can tell me how DHCP would report this
    def get_user(self,host,eventtime):
	return {}
    
    # This returns None unless someone can tell me how DHCP would report this
    def get_admin(self,host,eventtime):
	return {}
    
