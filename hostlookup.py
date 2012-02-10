#!/usr/bin/python -u
#
# This is hopefully an implementation of identify-pair, written in python
# It will need to implement the following subroutines to be considered
# complete:
#

from datetime import datetime, timedelta
import re
import sys
import hostdata


def usage () :
    print "Usage: "+sys.argv[0]+" {ip} {date} {time}"
    sys.exit(1)

if (len(sys.argv) != 4) :
    usage()
    
ip = sys.argv[1]
dstamp = sys.argv[2]
tstamp = sys.argv[3]

#
# This parses the event timestamp into something we can use
#
def parseISODate (dstamp,tstamp) :
    isodate = datetime.strptime(dstamp+" "+tstamp,"%Y-%m-%d %H:%M:%S")
    return isodate
                
#
# Now the action begins
#
isodate = parseISODate(dstamp,tstamp)
hl = hostdata.HostLookup()
resultHost = hl.lookup(ip,isodate)
if (resultHost):
    print ""
else:
    print "\nNo results found for %s %s %s" % (ip,dstamp,tstamp)
if (resultHost.ipv4addr):
    print "IPV4: %s" % resultHost.ipv4addr
if (resultHost.ipv6addr):
    print "IPV6: %s" % resultHost.ipv6addr
  
if (resultHost.hwaddr):
    print "Ethernet: %s" % resultHost.hwaddr
else:
    print "Ethernet: NONE FOUND"
print "Activity date: %s" % isodate.strftime("%Y-%m-%d %H:%M:%S")
if (resultHost.user):
    print "Primary user: %s" % str(resultHost.user)

if (resultHost.admin) :
    print "Admin contact: "+str(resultHost.admin)
