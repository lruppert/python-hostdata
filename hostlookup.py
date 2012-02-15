#!/usr/bin/env python
#
# This is a basic example script for using the hostdata framework.  It
# takes the IP/Timestamp info we normally get for an incident and parses
# out what it needs to do the lookup.  Then it prints the response.
#

from datetime import datetime, timedelta
import re
import sys
import hostdata


def usage () :
    print "Usage: "+sys.argv[0]+" {ip} {date} {time}"
    sys.exit(1)


#
# This parses the event timestamp into something we can use
#
def parse_ISO_date (dstamp,tstamp) :
    isodate = datetime.strptime(dstamp+" "+tstamp,"%Y-%m-%d %H:%M:%S")
    return isodate
                
#
# Now the action begins
#
def main() :
    if (len(sys.argv) != 4) :
        usage()
        
    ip = sys.argv[1]
    dstamp = sys.argv[2]
    tstamp = sys.argv[3]
    
    isodate = parse_ISO_date(dstamp,tstamp)
    
    hl = hostdata.HostLookup()
    resultHost = hl.lookup(ip,isodate)
    
    print "\nActivity date: %s" % isodate.strftime("%Y-%m-%d %H:%M:%S")
    if (not resultHost):
        print "No results found for %s %s %s" % (ip,dstamp,tstamp)
    if (resultHost.ipv4addr):
        print "IPV4: %s" % resultHost.ipv4addr
    if (resultHost.ipv6addr):
        print "IPV6: %s" % resultHost.ipv6addr
    
    if (resultHost.hwaddr):
        print "Ethernet: %s" % resultHost.hwaddr
    else:
        print "Ethernet: NONE FOUND"

    if (resultHost.user):
        print "Primary user: %s" % str(resultHost.user)
    
    if (resultHost.admin) :
        print "Admin contact: "+str(resultHost.admin)


if __name__ == "__main__" :
    main()
    