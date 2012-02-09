# Copyright (C) 2012 Lou Ruppert.  All Rights Reserved
# Author: Lou Ruppert <himself@louruppert.com>
#
# This code based heavily on the PluginManager example included with
# prelude-correlator
#

import sys,os

class Plugin(object):
    enable = True
    
    def get_hwaddr(self, hostobj, eventtime):
        return None
    
    def get_owner(self, hostobj, eventtime):
        return None
    
    def get_admin(self, hostobj, eventtime):
        return None



class PluginManager:
    __instances = []
    
    def __init_plugin(self, plugin):
        p = plugin()
        if p.enable:
            self.__instances.append(p)
            
        self._count = self._count + 1
        
    def __init__(self, hdconfig):
        self._count = 0
        
        sys.path.insert(0, hdconfig.get("Plugins","plugins_dir"))
        
        for file in os.listdir(hdconfig.get("Plugins","plugins_dir")):
            pl = __import__(os.path.splitext(file)[0], None, None,  [''])
            
        for plugin in Plugin.__subclasses__():
            self.__init_plugin(plugin)
            
    def get_plugin_count(self):
        return self._count
    
    def get_instance(self, plugin_name):
        for module in self.__instances:
            strmod = str(module)
            modname = strmod.split(".")[1].split(" ")[0]
            if modname == plugin_name.replace(' ', ''):
                return module
            
        