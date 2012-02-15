python-hostdata
===============

These are my efforts in combining a bunch of scripts I have at various sites
into something I can share with the community.

Background
----------

I have various hostname lookup tools I use for incident response.  Each is 
tailored heavily for the environment I run it in.  Why not combine them into
an awesome common framework?  This is my attempt.

Currently, there are a lot of hardcoded defaults and things specific to
certain environments.  In order to make the codebase more generic, I need to
abstract a bunch of stuff out.

Requirements
-------------

The data should be retrievable given only an IP and a timestamp, but
sometimes only a hardware address will be available.  

Different networks should permit different default orders of search plugins.  
For instance, one network might pull ip/timestamp lease information from a 
relational database.  Other might use Splunk and DHCP leases.  One might 
have user information included for an IP in syslog messages.  Another might 
have that information in a relational database or LDAP record.

Additional plugins should be configurable on the command line.  For instance,
if I want to do a search that includes other plugins that wouldn't otherwise
be the default (expensive computationally, perhaps) or if I want to exclude
a plugin, I should be able to do that without rewriting the config files.

Assumptions
-----------

For incident response, you need three classes of data, at minimum:

* Hardware address (so you can block it in infrastructure equipment or deny it a DHCP lease)
* User info (for notification)
* Admin user info (for creating tickets for sysadmins, notifications)

I've designed the host object to favor those classes, while allowing other
data to be conveniently attached.
