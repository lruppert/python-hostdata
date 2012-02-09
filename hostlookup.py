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

fmtipv4addr = str(ip)+" [dynamic]"
if (not resultHost.isDynamic()) :
    fmtipv4addr = str(resultHost.ipv4addr)+" [static ]"
print "\nDATA: "+isodate.strftime("%Y-%m-%d-%H:%M")+" "+fmtipv4addr
print "HDATA: [%s %s]" % (str(resultHost.hwaddr),str(resultHost.user))

if (resultHost.admin != None ) :
    print "HOSTREG: Admin contact: "+str(resultHost.admin)
if (resultHost.primary_hostname != None and resultHost.primary_hostname != '') :
    print "HOSTREG: Hostname: "+str(resultHost.primary_hostname)
if (resultHost.description != None and resultHost.description != '' 
    and resultHost.description != 'Quarantine stub') :
    print "HOSTREG: Description: "+str(resultHost.description)

print resultHost.getInfo("quarproc")
