# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 16:04:25 2020
@author: essie-adm-luan
"""

from datetime import datetime, timedelta
#import sensible
import time
import yaml
import zmq
# from sensible.util import ops
from multiprocessing import Process, Pipe, current_process
import socket





class msgManager:
    """
    This class is based on sensible's Manager class. It is responsible for
    sending and receiving messages between RIO and the COM interface for Vissim.
    """
    def __init__(self,configFile):
        
        with open(configFile,'r') as cfg:
            config_params = yaml.load(cfg)
            self.run_for = config_params['run_for']
            self.output_rate = config_params['output_rate']
            self.output_ip = config_params['output_ip']
            self.output_port = int(config_params["output_port"])
        
        # import pdb;pdb.set_trace()
        
        self._bsm_publisher = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._bsm_publisher.setblocking(0)
        self._dt = timedelta(milliseconds = 1000.0 / self.output_rate)


    def groupAndPublish(self, msgs):
        """
        Construct single string to send containing all data
        """
        sep = "^^^^"
        
        self._sensible_time = datetime.utcnow()
        
        final_msg = "{}:{}:{}.{}{}".format(self._sensible_time.hour, 
                self._sensible_time.minute, self._sensible_time.second,
                self._sensible_time.microsecond, sep)
        for m in msgs[0]:
            final_msg += "{}{}".format(m,sep)
        final_msg = final_msg[:-len(sep)]
        #self._bsm_publisher.sendto(final_msg, (self.output_ip, self.output_port))
        self._bsm_publisher.sendto(bytes(final_msg,"utf-8"),
                                   (self.output_ip, self.output_port))

        # print(final_msg)

    def messageBuilder(self,df):
        msgs = []
        for i in range(0,len(df)):
            msg = [0, #track id
                   df.iloc[i][0],
                   df.iloc[i][1],
                   df.iloc[i][2],
                   df.iloc[i][3],
                   df.iloc[i][4],
                   df.iloc[i][5],
                   df.iloc[i][6],
                   df.iloc[i][7],
                   df.iloc[i][8],
                   
                   
                    ]
            msgs.append(msg)
            return msgs
            
            
    def send(self,df):
        msgs = self.messageBuilder(df)
        self.groupAndPublish(msgs)