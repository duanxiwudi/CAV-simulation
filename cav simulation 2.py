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
from data_io import msgManager
import time
import pandas as pd
import auModel
import argparse
#--
# os.chdir(r"C:\Users\essie-adm-luan\Downloads\CAV-simulation-xixi\CAV-simulation-xixi");
# LC: saves you the effort of updating the working directory
currentDir = os.path.abspath(os.path.dirname(__file__)) 
os.chdir(currentDir)
#---simulation scenarios 
# 1 0.8 0.6 0.4 0.2
# 1 0.8 0.6 0.4 0.2
# 0.8 0.6 0.4 0.2
vc_ratio = 0.7
penetration_rate = 1
network_folder = "network2 - vc" + " " + str(vc_ratio) + " " + str(int(penetration_rate*100)) + "%"

#------------------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser()

# directory setting
parser.add_argument('--path_output_file', default = os.path.join(currentDir,"output"), help = "the directory of output file, the default is the current working directory ")
parser.add_argument('--path_of_network', default = os.path.join(currentDir, network_folder), help = "the directory of network file, including .inpx and .layx")

# simulation parameters setting
parser.add_argument('--version_VISSIM', default = "Vissim.Vissim.1000" , help = "1000 means Vissim 10")
parser.add_argument('--network_file', default = "network2.inpx" , help = "the name of VISSIM network file")
parser.add_argument('--layout_file', default = "network2.layx" , help = "the name of VISSIM layout file")

parser.add_argument('--duration', default = 36000 ,type = int, help = "simulation duration, unit in sim second")
parser.add_argument('--time_sleep', default = 0 ,type = float, help = "the sleep time between each time step of simulation")
# simulation traffic input setting 
parser.add_argument('--sb_volume', default = 1500 ,type = int, help = "traffic volume of southbound, vehicles / hr")
parser.add_argument('--nb_volume', default = 1500 ,type = int, help = "traffic volume of northbound, vehicles / hr")
parser.add_argument('--wb_volume', default = 1500 ,type = int, help = "traffic volume of westbound, vehicles / hr")
parser.add_argument('--eb_volume', default = 1500 ,type = int, help = "traffic volume of eastbound, vehicles / hr")
parser.add_argument('--CAV_rel_flow', default = 0.2 ,type = float, help = "the percentage of CAV volume")
parser.add_argument('--Desired_speed', default = 32 ,type = float, help = "the desired speed km/h")



# traffic model setting
parser.add_argument('--max_dec', default = -5.0 ,type = float, help = "the maximum deceleration, m / s^2")
parser.add_argument('--comf_dec', default = -3.5 ,type = float, help = "the comfortable deceleration, m / s^2")
parser.add_argument('--max_acc', default = 3 ,type = float, help = "the maximum acceleration, m / s^2")
parser.add_argument('--comf_acc', default = 2.5 ,type = float, help = "the comfortable acceleration, m / s^2")
parser.add_argument('--desired_speed_change_rate', default = 1 ,type = float, help = "used to define how driver would change to desired speed")
simulation = parser.parse_args()



left_lane = ['10012-1','10015-1','10011-1','10008-1']



# Loads the message manager that will send and receive the messages
msgCfgFile = os.path.join(currentDir, "data_io_config", "Local_RIO_Vissim.yml")
messageManager = msgManager(msgCfgFile)

sendMessage = False # this is to avoid breaking the code for now. 
f = open(simulation.path_output_file + "\\Trajectory.txt", "w")
f.close() 




# determine the type of data to be output --------------------------------------
# define the the column names of the output csv file

out_DataType_Traj = ['Time Stamp','Vehicle ID', 'Vehicle Type', 'Vehicle Length','Vehicle Front Coordinate','Vehicle Rear Coordinate','Speed','Acceleration','Headway','Lane']
# data type for signal output
out_DataType_Signal = ['Time Stamp','Signal head ID','Color','Latitude','Longitude','X','Y']
# data type for trajectory output
out_DataType_Traj_em = ['Time Stamp','Vehicle ID', 'Vehicle Type', 'Vehicle Length','Vehicle Front Coordinate','Vehicle Rear Coordinate','Speed','Acceleration','Headway']
# data type for CV (RIO) output
out_DataType_CVModel = ["No", "Pos", "Speed","pos_rms", "speed_rms", "veh_type", "veh_length", "max_accel", "max_decel"]
# the dictionary to change the default output data from vissim to required output data 
table_vehicle_type = dict({'100':"Passenger Car",'200':"Passenger Truck",'300':"Transit Bus",'400':"Tram",'630':"Passenger Car"})
table_signal_color = dict({'RED':0, 'AMBER':1, "GREEN":2}) 
# variables name to fetch the data from vissim
get_DataType_traj=('No', 'VehType','Length', 'CoordFront','CoordRear','Speed','Acceleration','Hdwy', 'Lane' )
get_DataType_signal=('No','SigState')
# // specify the vissim version here// 1000 means Vissim 10
Vissim= com.Dispatch(simulation.version_VISSIM)

#// input the lanes number and their corresponding start point's coordinate
'''
Lane 4: Eastbound,  (-181, -22)
Lane 3: Northbound  (-117, -141) 
Lane 1: Westbound   (60, -1) 
Lane 2: Southbound  (-165, 131) 
    
'''
eb_coor = (-181, -22)
nb_coor = (-117, -141)
wb_coor = (60, -1)
sb_coor = (165, 131)
eb_lane = 3
nb_lane = 4
wb_lane =1
sb_lane = 2
lane_to_cor = {eb_lane : eb_coor, nb_lane :  nb_coor, wb_lane: wb_coor, sb_lane : sb_coor }
store_speed = pd.DataFrame(columns = ["Vehicle ID","x speed", "y speed"])
vehicle_type_dict = {"Passenger Car" : 0}

#--------------------------------------------------------------
## Load a Vissim Network:
Filename                = os.path.join(simulation.path_of_network,simulation.network_file)
flag_read_additionally  = False # you can read network(elements) additionally, in this case set "flag_read_additionally" to true
Vissim.LoadNet(Filename, flag_read_additionally)
## Load a Layout:
Filename = os.path.join(simulation.path_of_network,simulation.layout_file)
Vissim.LoadLayout(Filename)
CAV = '630'
TRA_car = '100'
# Set vehicle input:
# // change the vehicles input here//
#==============================================================================
# Desired_speed = 70
# cav_flow_rate = simulation.CAV_rel_flow
# Vissim.Net.VehicleInputs.ItemByKey(1).SetAttValue('Volume(1)', simulation.eb_volume)
# Vissim.Net.VehicleInputs.ItemByKey(2).SetAttValue('Volume(1)', simulation.nb_volume)
# Vissim.Net.VehicleInputs.ItemByKey(3).SetAttValue('Volume(1)', simulation.wb_volume)
# Vissim.Net.VehicleInputs.ItemByKey(4).SetAttValue('Volume(1)', simulation.sb_volume)
# # Set vehicle composition:
#==============================================================================
  # //set the vehicles composition here//
Veh_composition_number = 1
Rel_Flows = Vissim.Net.VehicleCompositions.ItemByKey(Veh_composition_number).VehCompRelFlows.GetAll()
  # here the type 630 is the connected vehicles,type 100 is the normal vehicles
conventional_flow =  (1- penetration_rate) * 100 if penetration_rate != 1 else 0.001
Rel_Flows[0].SetAttValue('RelFlow',        conventional_flow) # Changing the relative flow
Rel_Flows[1].SetAttValue('RelFlow',        penetration_rate *100) # Changing the relative flow of the 2nd Relative Flow.

# 
#==============================================================================
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

def leading(lead_vehicle_id,data_set, start ):
    current_index = start
    while current_index >= 0:
        item = data_set[current_index]
        if item[0] == lead_vehicle_id:
            return [item[2],item[3],item[4]]
        current_index -= 1
    return False





 





##---------------------  setting for the simualtion
start_time = time.time()
traj_file = pd.DataFrame(columns = out_DataType_Traj_em)
traj_file.to_csv(simulation.path_output_file + "\\" + network_folder +"Trajectory_data.csv",  index = None,  mode='w')
signal_file = pd.DataFrame(columns = out_DataType_Signal)
signal_file.to_csv(simulation.path_output_file + "\\" + network_folder + "Signal_data.csv",  index = None,  mode='w')
log_col = ['time','No', 'VehType', 'pos','acceleration',' speed','leading pos', 'leading speed', 'leading acc','leading length','headway','Lane','design_acceleration', 'state']
log_file = pd.DataFrame(columns = log_col)
log_file.to_csv(simulation.path_output_file + "\\" + network_folder + "log.csv",  index = None,  mode='w')
#create the dataframe for output
CV_data = pd.DataFrame(columns = out_DataType_CVModel)


# initiate the simulation parameters
time_step=0 
pre_data_traj = pd.DataFrame(columns = out_DataType_Traj)
speed_vehicle = pd.DataFrame(columns = ["Vehicle ID", "Split Speed"])
## Read the signal coordinate data:
signal_input = pd.read_excel(simulation.path_output_file + "\\Signal data input.xlsx")
buffer =  2
#-------------------------------------- start simulation
#  Random_Seed = 42
#  Vissim.Simulation.SetAttValue('RandSeed', Random_Seed)
#

Vissim.Simulation.RunSingleStep()
while time_step <= simulation.duration:
    all_veh_attributes = Vissim.Net.Vehicles.GetMultipleAttributes((get_DataType_traj))  
# select_vehicles,add_data_traj, dataSet_traj  are for emission model purpose            
    all_veh_attributes=[veh for veh in all_veh_attributes]
# define and output the signal file here:    
    add_data_signal = pd.DataFrame(out_DataType_Signal)
    add_data_signal = pd.DataFrame([i for i in Vissim.Net.SignalHeads.GetMultipleAttributes(get_DataType_signal)])
    add_data_signal.insert(0,'Time Stamp',time_step)
    add_data_signal = pd.concat([add_data_signal, signal_input.loc[:,['latitude','longitude','x','y']]],1)
    add_data_signal.columns = out_DataType_Signal
#data conversion: including the unit and type
    add_data_signal.loc[:,'Color'] = add_data_signal.loc[:,'Color'].replace(table_signal_color)
    add_data_signal.loc[:,'Time Stamp'] = add_data_signal.loc[:,'Time Stamp']/10
#output              
    add_data_signal.to_csv(simulation.path_output_file + "\\" + network_folder + 'Signal_data.csv',   header = None,  index = None,  mode='a' )    
#output trajectory data here
# check if have the CVs in the network
    vehicle_ID = []
    vehicle_acc = []
    if not all_veh_attributes:
        print("no vehicles")
    else:
# collect and output the trajectory data
        add_data_traj = pd.DataFrame(all_veh_attributes)
        add_data_traj.insert(0,'Time Stamp',time_step)
        add_data_traj.columns=(out_DataType_Traj)
# log file initilization:
        log_file = pd.DataFrame(columns = log_col)
#data conversion: including the unit and type
        add_data_traj.loc[:,'Vehicle Type']=add_data_traj.loc[:,'Vehicle Type'].replace(table_vehicle_type)
        add_data_traj.loc[:,'Time Stamp']=add_data_traj.loc[:,'Time Stamp']/10
        add_data_traj.loc[:,'Speed']=add_data_traj.loc[:,'Speed'] / 1.6 # km/h to mile/h
        add_data_traj.loc[:,'Acceleration']= add_data_traj.loc[:,'Acceleration'] * 2.237 #meter/second /s  to mile/h/ s
        add_data_traj.loc[:,'Vehicle Length']= add_data_traj.loc[:,'Vehicle Length'] * 3.28084 #meter  to feet
        add_data_traj.loc[:,'Headway']= add_data_traj.loc[:,'Headway'] * 3.28084 #meter  to feet
# calculate the lateral and longitudinal speed        
        
        speed_cal_curr = add_data_traj.loc[:,["Vehicle ID" , "Vehicle Front Coordinate", "Lane"]]
        speed_cal_prev = pre_data_traj.loc[:,["Vehicle ID" , "Vehicle Front Coordinate", "Lane"]]        
        speed_cal_curr["x_coor_curr"] = [float(speed_cal_curr.loc[:, "Vehicle Front Coordinate"][i].split()[0]) for i in range(speed_cal_curr.shape[0]) ]
        speed_cal_curr["y_coor_curr"] = [float(speed_cal_curr.loc[:, "Vehicle Front Coordinate"][i].split()[1]) for i in range(speed_cal_curr.shape[0]) ]
        speed_cal_prev["x_coor_prev"] = [float(speed_cal_prev.loc[:, "Vehicle Front Coordinate"][i].split()[0]) for i in range(speed_cal_prev.shape[0]) ]
        speed_cal_prev["y_coor_prev"] = [float(speed_cal_prev.loc[:, "Vehicle Front Coordinate"][i].split()[1]) for i in range(speed_cal_prev.shape[0]) ]
        speed_data = pd.merge(speed_cal_curr,speed_cal_prev,   on = "Vehicle ID", how = "left")
# check if there are any vehicles just join the network, which does not have prev_coor values
        if (speed_data.loc[:, "x_coor_prev"].isnull()).any() :
            for i in speed_data.loc[speed_data.loc[:, "x_coor_prev"].isnull()].index:
                 lane_num = int(speed_data.loc[i, "Lane_x"].split('-')[0])
                 speed_data.loc[i, "x_coor_prev"] = lane_to_cor[lane_num][0]
                 speed_data.loc[i, "y_coor_prev"] = lane_to_cor[lane_num][1]
        
        speed_x = speed_data.loc[:, "x_coor_curr"] - speed_data.loc[:, "x_coor_prev"]
        speed_y = speed_data.loc[:, "y_coor_curr"] - speed_data.loc[:, "y_coor_prev"]
        speed_coor = [[speed_x[i], speed_y[i]] for i in range(len(speed_x))]
        add_data_traj["speed_coor"] = speed_coor
        CV_data = add_data_traj.loc[:, ["Vehicle ID", "Vehicle Front Coordinate","speed_coor", "nan", "nan", "Vehicle Type", "Vehicle Length"] ]
        CV_data["max_acc"] = simulation.max_acc
        CV_data["max_decce"] = simulation.max_dec
        CV_data["Vehicle Front Coordinate"] = [ i.split()[0:2] for i in (CV_data.loc[:, "Vehicle Front Coordinate"])]
        CV_data.replace(vehicle_type_dict, inplace = True)
        pre_data_traj = add_data_traj
    
#----------------------------------------------------------------------------------        
        add_data_traj = add_data_traj[out_DataType_Traj_em]
        add_data_traj.to_csv(simulation.path_output_file + "\\" + network_folder + 'Trajectory_data.csv',  header = None,  index = None,  mode='a' )
        
# run the simulation
        
# Method #5: Accessing all attributes directly using "GetMultipleAttributes" (even more faster)
# all_veh_attributes are for printing purpose 
        all_veh_attributes = Vissim.Net.Vehicles.GetMultipleAttributes(('No', 'VehType', 'acceleration', 'Speed', 'DistanceToSigHead'))
        for cnt in range(len(all_veh_attributes)):
            print ('%.f | %s  |  %s  |  %.2f  |  %.2f  |  %s' % (time_step,all_veh_attributes[cnt][0], all_veh_attributes[cnt][1], all_veh_attributes[cnt][2], all_veh_attributes[cnt][3], all_veh_attributes[cnt][4])) # only display the 2nd column)
## data_vehicles are for AV/CV modeling purpose        
        data_vehicles = Vissim.Net.Vehicles.GetMultipleAttributes(('No', 'VehType', 'length','Acceleration','Speed', 'Pos', 'Hdwy','LeadTargNo','LeadTargType','DistanceToSigHead', 'SignalState','Lane'))
        dist_stop = (simulation.Desired_speed / 3.6) **2 / 2 / -(simulation.comf_dec)
#data_vehicles: 0- No, 1-vehicle type, 2-length, 3-acceleration, 4-speed, 5-position, 6-headway, 7-lead No, 8- lead type, 9-distance to signal, 10- signal state, 11- lane
        for index in range(len(data_vehicles)):
# it is only used for CAV
            vehicle = data_vehicles[index]
            if (vehicle[1] != CAV):
                continue
# There are three mode for vehicles, free flow, signal controlled, and car following mode
# since the AV logic does not consider signal, we designed a signal controlled mode that vehicles are going to decelerate at comfortable deceleration rate when get close enough to signal head.
            dist_safe = (vehicle[4] / 3.6) **2 / 2 /  -(simulation.comf_dec)
            
            if (vehicle[8] == 'VEHICLE' and leading(vehicle[7],data_vehicles, index)):
                x_n = vehicle[5]
                v_n = vehicle[4]
                l_n_1, a_n_1, v_n_1 = leading(vehicle[7],data_vehicles,index) 
                x_n_1 = x_n + vehicle[6]
                ak = auModel.AV_Model( x_n, v_n / 3.6, x_n_1, v_n_1 /3.6, a_n_1, l_n_1).cal_acc()
                ak = min(ak, (simulation.Desired_speed/  3.6 - v_n / 3.6) * simulation.desired_speed_change_rate)
#==============================================================================
#                 if v_n_1 < 5 and vehicle[6] < dist_safe + buffer:
#                     ak = simulation.comf_dec
#                 if vehicle[9] < dist_safe + buffer and (vehicle[10] =='RED' or vehicle[10] =='AMBER'):    
#                     ak = simulation.comf_dec
#==============================================================================
                record = [[time_step, vehicle[0],vehicle[1], x_n,vehicle[3], v_n / 3.6, x_n_1, v_n_1 /3.6, a_n_1, l_n_1,x_n_1 - x_n,vehicle[11], ak, 'car following']]
                vehicle_ID.append(record[0][1])
                vehicle_acc.append(record[0][12]) 
            elif vehicle[9] < dist_safe + buffer and (vehicle[10] =='RED' or vehicle[10] =='AMBER'):    
                ak = simulation.comf_dec;
                record = [[time_step, vehicle[0], vehicle[1], vehicle[5],vehicle[3], vehicle[4] / 3.6,vehicle[5] + vehicle[9] , 0 , 0 ,0,vehicle[9], vehicle[11], ak, 'signal']]
                vehicle_ID.append(record[0][1])
                vehicle_acc.append(record[0][12]) 
            elif not vehicle[11] in left_lane:
                ak = min(simulation.comf_acc, (simulation.Desired_speed  - vehicle[4]) / 3.6 *simulation.desired_speed_change_rate )
                record = [[time_step, vehicle[0],vehicle[1], vehicle[5],vehicle[3], vehicle[4] / 3.6,0 , 0 ,0, 0 ,0 ,vehicle[11], ak, 'free']]
                vehicle_ID.append(record[0][1])
                vehicle_acc.append(record[0][12]) 
            else:
                record = [[time_step, vehicle[0],vehicle[1], vehicle[5],vehicle[3], vehicle[4] / 3.6,0 , 0 ,0, 0 ,0 ,vehicle[11], 999, 'vissim']]
               
            log_file = log_file.append(pd.DataFrame(record,  columns = log_col),ignore_index=True)
        
        ## update the traj file, here plus 0.01 
        traj = pd.DataFrame({'a':vehicle_ID,'b':vehicle_acc})
        traj.to_csv(simulation.path_output_file + "\\Trajectory.txt", header=None, index = None, sep=' ', mode='w')
        log_file.to_csv(simulation.path_output_file + "\\" + network_folder + "log.csv", header = None,  index = None,  mode='a')
        

        """
        LC: Xi,the function bellow will need a dataFrame containing the following 
        headers. Make sure that the headers names match. If you add extra headers it does not matter.
        
        
                 'No',
                 'pos', # List [UTM easting (float), UTM northing (float)]
                 'vel', # List [UTM easting dot (float), UTM northing dot (float)]
                 'pos_rms', # List [UtM easting (float), UTM northing (float)]
                 'vel_rms', # List [UTM easting dot (float), UTM northing dot (float)]
                 'veh_type', # 0 or 1 -- 0 for CNV, 1 for CAV
                 'veh_len', # float
                 'max_accel', # float
                 'max_decel', # float
                 ])
        """
        if sendMessage:
#            print('hi')
            if len(CV_data) > 0:
                messageManager.send(CV_data)
#                print(time_step)
#                if time_step == 10:
#                    print(time_step)
#                    import pdb;pdb.set_trace()
    time_step += 1   
    time.sleep(simulation.time_sleep)
    Vissim.Simulation.RunSingleStep()
        
'''
Signal control part

SC_number = 1
SG_number = 1
SignalController = Vissim.Net.SignalControllers.ItemByKey(SC_number)
SignalGroup = SignalController.SGs.ItemByKey(SG_number)
SignalGroup.SetAttValue("SigState", "GREEN")
SignalGroup.SetAttValue("ContrByCOM", False)

'''
Vissim.Simulation.Stop()

print(time.time() - start_time)
  
Filename = os.path.join(simulation.path_of_network, simulation.network_file)
Vissim.SaveNetAs(Filename)
Filename = os.path.join(simulation.path_of_network, simulation.layout_file)
Vissim.SaveLayout(Filename)

