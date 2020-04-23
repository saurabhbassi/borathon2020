import os
import pandas as pd
import logging


class AutomaticConfigTool(object):
    """
    This is the class which deals with loading and analysing the source vcenter data
    """
    def __init__(self,**kwargs):
        """
        This loads the default yaml config file and initialises the desired variables
        Kwargs: 
            config : by default config.yaml
            log_filename : by default is stdout
        """
        self._setup_logging(kwargs.get('log_filename',None))
        self.config = kwargs.get('config','config.yaml') #default config file is config.yaml
        self._config_load()
        logging.info("LOGGER INITIALISED")


    def _config_load(self):
        pass

    def _setup_logging(self,filename):
        """ Sets up global logging """
        if filename:
            logging.basicConfig(level=logging.DEBUG,
                                filename=filename,
                                format='%(asctime)s %(levelname)s: %(message)s',
                                datefmt='%Y-%m-%d %I:%M:%S %p')
        else:
            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s %(levelname)s: %(message)s',
                                datefmt='%Y-%m-%d %I:%M:%S %p')

    def get_host_ip_and_datastore(self,user_config):
        pass

    
    
    