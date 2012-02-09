# Copyright (C) 2012 Lou Ruppert.  All Rights Reserved
# Author: Lou Ruppert <himself@louruppert.com>
#

from hostdata.PluginManager import Plugin

#
# This class serves as the example as well as a useful endpoint to searches
# or a means of suppressing them.
class Test(Plugin):
    def get_hwaddr(self,host,eventtime):
	return "deadbeefcafe"

    def get_user(self,host,eventtime):
	return "testuser"
    
    def get_admin(self,host,eventtime):
	return "testadmn"
    
