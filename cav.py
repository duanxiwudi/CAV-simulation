# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 22:22:43 2019

@author: xiduan
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 10:25:09 2018

@author: xiduan
"""
import win32com.client as com
import os 
import time
import pandas as pd
import auModel


# determine the type of data to be output
# define the the column names of the output csv file
out_DataType_Traj=['Time Stamp','Vehicle ID', 'Vehicle Type', 'Vehicle Length','Vehicle Front Coordinate','Vehicle Rear Coordinate','Speed','Acceleration','Headway']
out_DataType_Signal=['Time Stamp','Signal head ID','Color','Latitude','Longitude','X','Y']
# the dictionary to change the default output data from vissim to required output data 
table_vehicle_type = dict({'100':"Passenger Car",'200':"Passenger Truck",'300':"Transit Bus",'400':"Tram",'630':"Passenger Car"})
table_signal_color = dict({'RED':0, 'AMBER':1, "GREEN":2}) 
# variables name to fetch the data from vissim
get_DataType_traj=('No', 'VehType','Length', 'CoordFront','CoordRear','Speed','Acceleration','Hdwy')
get_DataType_signal=('No','SigState')
# // specify the vissim version here// 1000 means Vissim 10
Vissim= com.Dispatch("Vissim.Vissim.1000")

#User input---------------------------------------------------- 
# //input your fold directory which contains the Vissim file here//
Path_of_COM_Basic_Commands_network = "C:\\Users\\xiduan\\OneDrive - University of Florida\\UF\\research\\2.Vissim AV&CV\\network" 
# // write your output fold directory here//
Path_output_file = "C:\\Users\\xiduan\\OneDrive - University of Florida\\UF\\research\\2.Vissim AV&CV\\Document\\Task1\\"
# //input your network file and layout file name here//
Network_file='network2.inpx'
Layout_file='network2.layx'

# //input your simulation duration here//
simulation_duration=3600
#--------------------------------------------------------------
## Load a Vissim Network:
Filename                = os.path.join(Path_of_COM_Basic_Commands_network,Network_file)
flag_read_additionally  = False # you can read network(elements) additionally, in this case set "flag_read_additionally" to true
Vissim.LoadNet(Filename, flag_read_additionally)
## Load a Layout:
Filename = os.path.join(Path_of_COM_Basic_Commands_network, Layout_file)
Vissim.LoadLayout(Filename)


CAV = '630'
# Set vehicle input:
# // change the vehicles input here//
VI_number   = 1 # VI = Vehicle Input
new_volume  = 1500 # vehicles per hour
Vissim.Net.VehicleInputs.ItemByKey(VI_number).SetAttValue('Volume(1)', new_volume)

# Set vehicle composition:
# //set the vehicles composition here//
Veh_composition_number = 1
Desired_speed = 70
Rel_Flows = Vissim.Net.VehicleCompositions.ItemByKey(Veh_composition_number).VehCompRelFlows.GetAll()
# here the type 630 is the connected vehicles,type 100 is the normal vehicles
Rel_Flows[0].SetAttValue('VehType',        100) # Changing the vehicle type
Rel_Flows[1].SetAttValue('VehType',        CAV) # Changing the vehicle type
Rel_Flows[0].SetAttValue('DesSpeedDistr',   Desired_speed) # Changing the desired speed distribution
Rel_Flows[1].SetAttValue('DesSpeedDistr',   Desired_speed) # Changing the desired speed distribution
Rel_Flows[0].SetAttValue('RelFlow',        50) # Changing the relative flow
Rel_Flows[1].SetAttValue('RelFlow',        50) # Changing the relative flow of the 2nd Relative Flow.

## function to calculate the distance
# a, b are two list contain coordinate like [x,y,z]
def cal_dis(coord1,coord2):
    return ((float(coord1[0])-float(coord2[0]))**2+(float(coord1[1])-float(coord2[1]))**2)**0.5

## function to find the vehicles ID within certain range/radiums
# Num is the vehicles ID and Radiums is the range 
def Vehicle_within(Num, Radiums,add_data):
    current_coord=add_data.loc[add_data['No']==Num,'CoordFront'][0]
    current_coord=current_coord.split()
    vehicle_list=[]
    No_=add_data.loc[add_data['No']!=Num, 'No']    
    Coor_=[i.split() for i in add_data.loc[add_data['No']!=Num, 'CoordFront']]
    look_table=dict(zip(No_,Coor_))
    for i in No_:
        if cal_dis(look_table[i],current_coord)<=Radiums:
            vehicle_list.append(i)
    return vehicle_list

def leading(lead_vehicle_id,data_set ):
    for item in data_set:
        if item[0] == lead_vehicle_id:
            return [item[2],item[3],item[4],item[5]]
    return False





 





##---------------------  setting for the simualtion

#create the dataframe for output
log_col = ['time','No', 'VehType', 'pos','acceleration',' speed','leading pos', 'leading speed', 'leading acc','leading length','headway','design_acceleration', 'state']
log_file = pd.DataFrame(columns = log_col)
log_file.to_csv(Path_output_file + "log.csv",  index = None,  mode='w')
dataSet_traj=pd.DataFrame(columns=out_DataType_Traj)
# initiate the simulation parameters
time_step=0 
time_sleep=0
simulation_duration=3600
max_dec = -5
# comfortable deceleration
comf_dec = -3.4
max_acc = 3
# comfortable acceleration
comf_acc = 2.5

#-------------------------------------- start simulation
while time_step < simulation_duration:
    all_veh_attributes = Vissim.Net.Vehicles.GetMultipleAttributes((get_DataType_traj))              
    select_vehicles=[veh for veh in all_veh_attributes if veh[1]=='630']
# define and output the signal file here:    
   
#output trajectory data here
# check if have the CVs in the network
    if not select_vehicles:
        time_step+=1
        time.sleep(time_sleep)
        Vissim.Simulation.RunSingleStep()
    else:
# collect and output the trajectory data
        Vissim.Simulation.RunSingleStep()
        time_step += 1
        vehicle_ID = []
        vehicle_acc = []
        add_data_traj = pd.DataFrame(select_vehicles)
        add_data_traj.insert(0,'Time Stamp',time_step)
        add_data_traj.columns=(out_DataType_Traj)
# log file initilization:
        log_file = pd.DataFrame(columns = log_col)
#data conversion: including the unit and type
        add_data_traj.loc[:,'Vehicle Type']=add_data_traj.loc[:,'Vehicle Type'].replace(table_vehicle_type)
        add_data_traj.loc[:,'Time Stamp']=add_data_traj.loc[:,'Time Stamp']/10
        add_data_traj.loc[:,'Acceleration']= add_data_traj.loc[:,'Acceleration']/1.46667 #feet/second /s  to mile/h/ s
        dataSet_traj=dataSet_traj.append(add_data_traj,ignore_index = True)
        dataSet_traj=dataSet_traj[out_DataType_Traj]                
        dataSet_traj.to_csv(Path_output_file+'Trajectory_data.csv',  index=False )
        
# run the simulation
        
        # Method #5: Accessing all attributes directly using "GetMultipleAttributes" (even more faster)
        all_veh_attributes = Vissim.Net.Vehicles.GetMultipleAttributes(('No', 'VehType', 'acceleration', 'Speed', 'DistanceToSigHead'))
        for cnt in range(len(all_veh_attributes)):
            print ('%s  |  %s  |  %.2f  |  %.2f  |  %s' % (all_veh_attributes[cnt][0], all_veh_attributes[cnt][1], all_veh_attributes[cnt][2], all_veh_attributes[cnt][3], all_veh_attributes[cnt][4])) # only display the 2nd column)
        
        data_vehicles = Vissim.Net.Vehicles.GetMultipleAttributes(('No', 'VehType', 'length','Acceleration','Speed', 'Pos', 'Hdwy','LeadTargNo','LeadTargType','DistanceToSigHead', 'SignalState'))
        dist_stop = (Desired_speed / 3.6) **2 / 2 / -comf_dec
# 0- No, 1-vehicle type, 2-length, 3-acceleration, 4-speed, 5-position, 6-headway, 7-lead No, 8- lead type, 9-distance to signal, 10- signal state
        for vehicle in data_vehicles:
            if (vehicle[1] != CAV):
                continue
            dist_safe = (vehicle[4] / 3.6) **2 / 2 / -comf_dec
            if (vehicle[8] == 'VEHICLE' and leading(vehicle[7],data_vehicles)):
                x_n = vehicle[5]
                v_n = vehicle[4]
                l_n_1, a_n_1, v_n_1,x_n_1 = leading(vehicle[7],data_vehicles) 
                ak = auModel.AV_Model( x_n, v_n / 3.6, x_n_1, v_n_1 /3.6, a_n_1, l_n_1).cal_acc() 
                if v_n_1 == 0 and vehicle[6] < dist_safe + 5:
                    ak = comf_dec
                record = [[time_step, vehicle[0],vehicle[1], x_n,vehicle[3], v_n / 3.6, x_n_1, v_n_1 /3.6, a_n_1, l_n_1,x_n_1 - x_n, ak, 'car following']]
            elif vehicle[9] <dist_safe + 5 and vehicle[10] =='RED':
                ak = comf_dec;
                record = [[time_step, vehicle[0],vehicle[1], vehicle[5],vehicle[3], vehicle[4] / 3.6,vehicle[5] + vehicle[9] , 0 , 0 ,0,vehicle[9], ak, 'signal']]
            else:
                ak = min(comf_acc, (Desired_speed  - vehicle[4]) / 3.6 *0.58 if vehicle[4] < Desired_speed else 0 )
                record = [[time_step, vehicle[0],vehicle[1], vehicle[5],vehicle[3], vehicle[4] / 3.6,0 , 0 ,0, 0 ,0 , ak, 'free']]
            log_file = log_file.append(pd.DataFrame(record,  columns = log_col),ignore_index=True)
            vehicle_ID.append(record[0][1])
            vehicle_acc.append(record[0][11])  
        time.sleep(time_sleep)
        ## update the traj file, here plus 0.01 
        traj = pd.DataFrame({'a':vehicle_ID,'b':vehicle_acc})
        traj.to_csv(Path_output_file + "Trajectory.txt", header=None, index = None, sep=' ', mode='w')
        log_file.to_csv(Path_output_file + "log.csv", header = None,  index = None,  mode='a')
       









