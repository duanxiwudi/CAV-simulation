# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 11:17:55 2019
 STride
@author: xiduan
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 20:21:47 2019

@author: xiduan
"""
import numpy as np
class AV_Model ():
    
    def __init__(self, x_n, v_n, x_n_1, v_n_1, a_n_1, l_n_1, d_n = -6, d_n_1= -6, k = 1, k_a = 1, k_v = 0.58, k_d = 0.1,de_x = 300, acc_max = 3 ,tau = 0.1 ):
        '''
        vehicle n is the subject, vehicle n-1 is the leading vehicle
       :param x_n 
           location of vehicle n
       :param v_n 
           the speed of vehicles n
       :param x_n_1
            the location of vehicles n-1
       :param v_n_1
            the speed of vehicles n-1
       :param a_n_1
            the acceleration of vehicles n-1 
       :param l_n_1
            the length of vehicles n-1
       :param d_n 
           the maximum deceleration of vehicles n
       :param d_n_1 
           the maximum deceleration of vehicles n-1
       :param k default: 1.0 
          model parameter
       :param k_a default: 1.0
          model parameter
       :param k_v default: 0.58
           model parameter
       :param k_d default: 0.1
           model parameter
       :param de_x 
           the maximum detection distance of autonomous vehicle
       :param acc_max
           the maximum acceleration of vehicle n
       :param tau 
           the reaction time of AV
        '''
        self.tau = tau 
        self.x_n = x_n
        self.v_n = v_n
        self.x_n_1 = x_n_1
        self.v_n_1 = v_n_1
        self.a_n_1 = a_n_1
        self.l_n_1 = l_n_1
        self.d_n = d_n
        self.d_n_1 = d_n_1
        self.k = k
        self.k_a = k_a 
        self.k_v = k_v 
        self.k_d = k_d 
        self.de_x = de_x
        self.acc_max = acc_max
    
    def cal_acc(self):
        
        s_safe = (self.v_n_1)**2 / 2* (1 / self.d_n -  1 / self.d_n_1)
        
        s_system =  self.v_n *  self.tau
        s_min = 2
        s_ref = np.max([s_system,s_safe,s_min])
        
        acc_t  =  self.k_a *  self.a_n_1  +  self.k_v * ( self.v_n_1 - self.v_n) + self.k_d * ((self.x_n_1 - self.x_n)  - s_ref)
        # delta_x is the space
        delta_x = np.min([(self.x_n_1 - self.x_n - self.l_n_1) + self.v_n * self.tau - self.v_n_1**2 /2 / self.d_n_1,self.de_x])
        # v_max is the maximum safe speed
        v_max = (-2*self.d_n_1 * delta_x)**0.5
        
        acc = np.min([acc_t, self.k * (v_max - self.v_n),self.acc_max])
        
        
      
        
        return acc
    
    



