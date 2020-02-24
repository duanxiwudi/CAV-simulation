/*==========================================================================*/
/*  DriverModel.cpp                                  DLL Module for VISSIM  */
/*                                                                          */
/*  Interface module for external driver models.                            */
/*  Dummy version that does nothing (uses Vissim's internal model).         */
/*                                                                          */
/*  Version of 2018-09-13                                   XI DUAN			 */
/*==========================================================================*/

#include "DriverModel.h"
#include <fstream>	//std:ifstream
#include <iostream>
#include <string>
#include <sstream>
#include <algorithm>
using namespace std;

/*==========================================================================*/
// # 1 user working directory

/*Trajectory.txt, format as vehicles_ID, Vehicle_acceleration */
char inputPath[] = "P:\\STRIDE on VISSIM CAV\\code\\output\\Trajectory.txt";
char outputPath[] = "P:\\STRIDE on VISSIM CAV\\code\\output\\";

// # 2 initial parameters
double time_step = 0;

long    vehicle_color = RGB(0, 0, 0);

// # 3 output parameters
// note: the parameters with preceding Veh_ is output
long		VehID;
//the input_ID and input_acceleration will read from txt from python, **note: the size of the array
long	input_ID[1000];
double  input_acceleration[1000];
double	veh_speed = 0;
double  desired_velocity     = 20;
long    turning_indicator    = 0;
long		lane = 0;
double	laneWidth;
double veh_lat_po = 0;
double time = 0;
// the value sent by vissim

double  veh_acceleration = 0;
double veh_lane_angle = 0;
long veh_target_lane = 0;
long veh_active_lane = 0;
// index_num and size_num are used to assign the acceleration to corresponding vehicle ID  
int index_num = 0;
int size_num = 0;
// #3 control parameters, this block is not used
// these are arrays used for latitude and longitude trajectory control
/*double  desired_acceleration[] = { 3,3,3,3,3,3,3,3,	1.5,	1.2,	1.5,	1.2,	1.2,	0.8,	0.8,	0.8,	0.8,	0.8,	0.7,	0.7,	0.7,	0.7,	0.7,	0.7,	0.5,	0.5,	0.5,	0.3,	0.3,	0.2,	0.2,	0.2,	-3,	-3,	-3,	-2,	-2,	-2,	-1.7,	-1.6,	-1.6,	-1.5,	-1.5,	-1.5,	-1,	-0.5,	-0.5,	-0.2,	-0.1,	1,	1,	1,	1.2,	1.2,	1.2,	1.2,	-1,	-1,	0,	0
};
double  desired_lane_angle[] = { 1,	1,	1,	1,	1,	1,	1,	1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	1,	1,	1,	1,	1,	1,	1,	1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	1,	1,	1,	1,	1,	1,	1,	1,	1,	1,	1,	1
};
long    active_lane_change[] = { 1,	1,	1,	1,	1,	1,	1,	1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	1,	1,	1,	1,	1,	1,	1,	1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	1,	1,	1,	1,	1,	1,	1,	1,	1,	1,	1,	1
};
long    rel_target_lane[] = { 1,	1,	1,	1,	1,	1,	1,	1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	1,	1,	1,	1,	1,	1,	1,	1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	-1,	1,	1,	1,	1,	1,	1,	1,	1,	1,	1,	1,	1
};*/
int	curren_time = -1;
double  lane_angle =1;
long    active_lane = 0;
long    target_lane = 0;
double desired_acceleration = 0;
// define the input file of acceleration input
ifstream myfile;


// Pointers used for the opening of ".txt" files.
// file_rm used for general log
// file_lt_in show the value pass from Vissim
// file_lt_out shows the value used in the dll
FILE *file_rm = NULL;
FILE *file_lt_in = NULL;
FILE *file_lt_out = NULL;

// The function is used to return the index of key in the array, find the acceleration for the corresponding ID
int find(long arr[], int n, long key)
{
	int index = -999;

	for (int i = 0; i < n; i++){
		if (arr[i] == key){
			index = i;
			break;
		} 
	}
	return index;
}

/*==========================================================================*/

BOOL APIENTRY DllMain (HANDLE  hModule,
                       DWORD   ul_reason_for_call,
                       LPVOID  lpReserved)
{
  switch (ul_reason_for_call) {
      case DLL_PROCESS_ATTACH:
      case DLL_THREAD_ATTACH:
      case DLL_THREAD_DETACH:
      case DLL_PROCESS_DETACH:
         break;
  }
  return TRUE;
}

/*==========================================================================*/

DRIVERMODEL_API  int  DriverModelSetValue (long   type,
                                           long   index1,
                                           long   index2,
                                           long   long_value,
                                           double double_value,
                                           char   *string_value)
{
  /* Sets the value of a data object of type <type>, selected by <index1> */
  /* and possibly <index2>, to <long_value>, <double_value> or            */
  /* <*string_value> (object and value selection depending on <type>).    */
  /* Return value is 1 on success, otherwise 0.                           */

  switch (type) {
    case DRIVER_DATA_PATH                   :
		
		//will need to update file path
		strcat(outputPath, "AV_Log.txt");
		//strcat(outputPath, "lateral_in.txt");
		//strcat(outputPath, "lateral_out.txt");
		fopen_s(&file_rm, outputPath, "wt");
		//fopen_s(&file_lt_in, "C:\\Users\\xiduan\\OneDrive - University of Florida\\UF\\research\\2.Vissim AV&CV\\Dll code\\lateral_in.txt", "wt");
		//fopen_s(&file_lt_out, "C:\\Users\\xiduan\\OneDrive - University of Florida\\UF\\research\\2.Vissim AV&CV\\Dll code\\lateral_out.txt", "wt");
		//Statement to write data to the text file. To change type of data output, change the character after %: s -string; d - long; f - double
		if (file_rm != NULL) { fprintf_s(file_rm, "101 DRIVER_DATA_PATH: \t%s, \n", string_value); }
    case DRIVER_DATA_TIMESTEP               :
		time_step = double_value;
    case DRIVER_DATA_TIME                   :
		time = double_value;
      return 1;
    case DRIVER_DATA_USE_UDA                :
      return 0; /* doesn't use any UDAs */
                /* must return 1 for desired values of index1 if UDA values are to be sent from/to Vissim */
    case DRIVER_DATA_VEH_ID                 :

	// store the VehID information here
		VehID = long_value;
		// read the trajectory from the txt file defined before

		
	
		
		return 1;

    case DRIVER_DATA_VEH_LANE               :
		// get the current lane number from vissim
		lane = long_value;
		return 1;
    case DRIVER_DATA_VEH_ODOMETER           :
    case DRIVER_DATA_VEH_LANE_ANGLE         :
		veh_lane_angle = double_value;
		return 1;
    case DRIVER_DATA_VEH_LATERAL_POSITION   :
		// get the current lateral position from vissim
		veh_lat_po = double_value;
		return 1;
    case DRIVER_DATA_VEH_VELOCITY           :
		// get the speed
		veh_speed = double_value;
		return 1;
    case DRIVER_DATA_VEH_ACCELERATION       :
		// get the acceleration
		veh_acceleration = double_value;
		return 1;
    case DRIVER_DATA_VEH_LENGTH             :
    case DRIVER_DATA_VEH_WIDTH              :
    case DRIVER_DATA_VEH_WEIGHT             :
    case DRIVER_DATA_VEH_MAX_ACCELERATION   :
      return 1;
    case DRIVER_DATA_VEH_TURNING_INDICATOR  :
      turning_indicator = long_value;
      return 1;
    case DRIVER_DATA_VEH_CATEGORY           :
    case DRIVER_DATA_VEH_PREFERRED_REL_LANE :
    case DRIVER_DATA_VEH_USE_PREFERRED_LANE :
      return 1;
    case DRIVER_DATA_VEH_DESIRED_VELOCITY   :
      desired_velocity = double_value;
      return 1;
    case DRIVER_DATA_VEH_X_COORDINATE       :
    case DRIVER_DATA_VEH_Y_COORDINATE       :
    case DRIVER_DATA_VEH_Z_COORDINATE       :
    case DRIVER_DATA_VEH_REAR_X_COORDINATE  :
    case DRIVER_DATA_VEH_REAR_Y_COORDINATE  :
    case DRIVER_DATA_VEH_REAR_Z_COORDINATE  :
    case DRIVER_DATA_VEH_TYPE               :
      return 1;
    case DRIVER_DATA_VEH_COLOR              :
      vehicle_color = long_value;
      return 1;
    case DRIVER_DATA_VEH_CURRENT_LINK       :
      return 0; /* (To avoid getting sent lots of DRIVER_DATA_VEH_NEXT_LINKS messages) */
                /* Must return 1 if these messages are to be sent from VISSIM!         */
    case DRIVER_DATA_VEH_NEXT_LINKS         :
    case DRIVER_DATA_VEH_ACTIVE_LANE_CHANGE :
		veh_active_lane = long_value;
		return 1;
    case DRIVER_DATA_VEH_REL_TARGET_LANE    :
		veh_target_lane = long_value;
		return 1;
    case DRIVER_DATA_VEH_INTAC_STATE        :
    case DRIVER_DATA_VEH_INTAC_TARGET_TYPE  :
    case DRIVER_DATA_VEH_INTAC_TARGET_ID    :
    case DRIVER_DATA_VEH_INTAC_HEADWAY      :
    case DRIVER_DATA_VEH_UDA                :
    case DRIVER_DATA_NVEH_ID                :
    case DRIVER_DATA_NVEH_LANE_ANGLE        :
    case DRIVER_DATA_NVEH_LATERAL_POSITION  :
    case DRIVER_DATA_NVEH_DISTANCE          :
    case DRIVER_DATA_NVEH_REL_VELOCITY      :
    case DRIVER_DATA_NVEH_ACCELERATION      :
    case DRIVER_DATA_NVEH_LENGTH            :
    case DRIVER_DATA_NVEH_WIDTH             :
    case DRIVER_DATA_NVEH_WEIGHT            :
    case DRIVER_DATA_NVEH_TURNING_INDICATOR :
    case DRIVER_DATA_NVEH_CATEGORY          :
    case DRIVER_DATA_NVEH_LANE_CHANGE       :
    case DRIVER_DATA_NVEH_TYPE              :
    case DRIVER_DATA_NVEH_UDA               :
    case DRIVER_DATA_NVEH_X_COORDINATE      :
    case DRIVER_DATA_NVEH_Y_COORDINATE      :
    case DRIVER_DATA_NVEH_Z_COORDINATE      :
    case DRIVER_DATA_NVEH_REAR_X_COORDINATE :
    case DRIVER_DATA_NVEH_REAR_Y_COORDINATE :
    case DRIVER_DATA_NVEH_REAR_Z_COORDINATE :
    case DRIVER_DATA_NO_OF_LANES            :
    case DRIVER_DATA_LANE_WIDTH             :
    case DRIVER_DATA_LANE_END_DISTANCE      :
    case DRIVER_DATA_CURRENT_LANE_POLY_N    :
    case DRIVER_DATA_CURRENT_LANE_POLY_X    :
    case DRIVER_DATA_CURRENT_LANE_POLY_Y    :
    case DRIVER_DATA_CURRENT_LANE_POLY_Z    :
    case DRIVER_DATA_RADIUS                 :
    case DRIVER_DATA_MIN_RADIUS             :
    case DRIVER_DATA_DIST_TO_MIN_RADIUS     :
    case DRIVER_DATA_SLOPE                  :
    case DRIVER_DATA_SLOPE_AHEAD            :
    case DRIVER_DATA_SIGNAL_DISTANCE        :
    case DRIVER_DATA_SIGNAL_STATE           :
    case DRIVER_DATA_SIGNAL_STATE_START     :
    case DRIVER_DATA_SPEED_LIMIT_DISTANCE   :
    case DRIVER_DATA_SPEED_LIMIT_VALUE      :
      return 1;
    case DRIVER_DATA_DESIRED_ACCELERATION :
		desired_acceleration = double_value;
		return 1;
    case DRIVER_DATA_DESIRED_LANE_ANGLE :
		lane_angle = double_value;
      return 1;
    case DRIVER_DATA_ACTIVE_LANE_CHANGE :
     // get the active lane change value from vissim
		active_lane = long_value;
      return 1;
    case DRIVER_DATA_REL_TARGET_LANE :
		target_lane = long_value;
      return 1;
    default :
      return 0;
  }
}

/*--------------------------------------------------------------------------*/

DRIVERMODEL_API  int  DriverModelGetValue (long   type,
                                           long   index1,
                                           long   index2,
                                           long   *long_value,
                                           double *double_value,
                                           char   **string_value)
{
  /* Gets the value of a data object of type <type>, selected by <index1> */
  /* and possibly <index2>, and writes that value to <*double_value>,     */
  /* <*float_value> or <**string_value> (object and value selection       */
  /* depending on <type>).                                                */
  /* Return value is 1 on success, otherwise 0.                           */

  switch (type) {
    case DRIVER_DATA_STATUS :
      *long_value = 0;
      return 1;
    case DRIVER_DATA_VEH_TURNING_INDICATOR :
      *long_value = turning_indicator;
      return 1;
    case DRIVER_DATA_VEH_DESIRED_VELOCITY   :
	
		/*if (find(input_ID, size_num, VehID) == -999) {
			*double_value = 2;
		}
		else {
			
			
			index_num = find(input_ID, size_num, VehID);
			*double_value = 10;
		} */
		*double_value = desired_velocity;

      return 1;
    case DRIVER_DATA_VEH_COLOR :
      *long_value = vehicle_color;
      return 1;
    case DRIVER_DATA_VEH_UDA :
      return 0; /* doesn't set any UDA values */
    case DRIVER_DATA_WANTS_SUGGESTION :
	
		*long_value = 1;
      return 1;
    case DRIVER_DATA_DESIRED_ACCELERATION :

		// also need to change the directory
		myfile.open(inputPath);

		/*read the trajectory.txt file here, store the ID its corresponding acceleration as array*/
		for (int i = 0; !myfile.eof(); i++) {

			myfile >> input_ID[i] >> input_acceleration[i];
			size_num = i;
		}
		myfile.close();

		/*if the Vehicle ID is not in the trajectory.txt, pass the default value from VISSIM or constant 0.3 to it.*/
		if (find(input_ID, size_num, VehID) == -999) {
			*double_value = desired_acceleration;
		} else {
			/* if we could find corresponding vehicle, pass the designed acceleration to the correspoing vehicle.*/
		 index_num = find(input_ID, size_num, VehID);
		*double_value = input_acceleration[index_num];
		} 
		
		return 1;
    case DRIVER_DATA_DESIRED_LANE_ANGLE :
     // *double_value = desired_lane_angle[curren_time];
	//*double_value = lane_angle;

	
		
			*double_value = lane_angle;
		
		
		return 1;
    case DRIVER_DATA_ACTIVE_LANE_CHANGE :
      //*long_value = active_lane_change[curren_time];
		//*long_value =1;
		/*if (veh_lane_num == 2 && veh_lat_po == 0.4) {
			*long_value = 0;
		}
		else {
			*long_value = 1;
		} */
		*long_value = active_lane;
		/*if (curren_time == 10) {
			*long_value = 1;
		}
		else if (curren_time == 80) {
			*long_value = -1;
		}
		*/
      return 1;
    case DRIVER_DATA_REL_TARGET_LANE :
    // *long_value = rel_target_lane[curren_time];
		
		/*if (curren_time == 10) {
			*long_value = 1;
		}
		else if (curren_time == 80) {
			*long_value = -1;
		}
		*/
		*long_value = target_lane;
		return 1;
    case DRIVER_DATA_SIMPLE_LANECHANGE :
      *long_value = 1;
      return 1;
    case DRIVER_DATA_USE_INTERNAL_MODEL:
      *long_value = 0; /* must be set to 0 if external model is to be applied */
      return 1;
    case DRIVER_DATA_WANTS_ALL_NVEHS:
      *long_value = 0; /* must be set to 1 if data for more than 2 nearby vehicles per lane and upstream/downstream is to be passed from Vissim */
      return 1;
    case DRIVER_DATA_ALLOW_MULTITHREADING:
      *long_value = 0; /* must be set to 1 to allow a simulation run to be started with multiple cores used in the simulation parameters */
      return 1;
    default:
      return 0;
  }
}

/*==========================================================================*/

DRIVERMODEL_API  int  DriverModelExecuteCommand (long number)
{
  /* Executes the command <number> if that is available in the driver */
  /* module. Return value is 1 on success, otherwise 0.               */

  switch (number) {
    case DRIVER_COMMAND_INIT :
		if (file_rm != NULL) { fprintf_s(file_rm, "**Initialization:\t%d time_step\t%.2f time: %.1f\n:", VehID,time_step,time); }
		if (file_rm != NULL) { fprintf_s(file_rm, "Time: %.1f\tVehicle ID: %d\tLane: %d\tSpeed: %.4f\tAccel: %.4f\tLC_angle %0.3f\n", time, VehID, lane, veh_speed, veh_acceleration, veh_lane_angle); }
		
		
		return 1;
    case DRIVER_COMMAND_CREATE_DRIVER :
		if(file_rm != NULL) { fprintf_s(file_rm, "*******************Create Driver ID:\t%d time: %.1f\n", VehID,time); }
		curren_time = -1;
		
      return 1;
    case DRIVER_COMMAND_KILL_DRIVER :
		if (file_rm != NULL) { fprintf_s(file_rm, "*******************Kill Driver ID:\t%d \n", VehID); }
		return 1;
    case DRIVER_COMMAND_MOVE_DRIVER :
		myfile.open(inputPath);
		
		for (int i = 0; !myfile.eof(); i++) {
			
			myfile >>input_ID[i] >> input_acceleration[i];
			size_num = i;
		}
		myfile.close();
		
		if (file_rm != NULL) { fprintf_s(file_rm, "ID: %d\t acceleration: %f.3\t speed: %d\t\n", VehID, veh_acceleration,size_num); }
		if (file_lt_out != NULL) { fprintf_s(file_lt_out, "acc1: %.3f \t acc2: %.3f\t acc3: %.3f\tacc4: %.3f\tacc5: %.3f\tacc6: %.3f\n", input_acceleration[0], input_acceleration[1], input_acceleration[2], input_acceleration[3], input_acceleration[4], input_acceleration[5]); }
		if (file_lt_in != NULL) { fprintf_s(file_lt_in, "ID 1 %d\t ID 2 %d\tID 3 %d\tID 4 %d\tID 5 %d\tID 6 %d\t\n",input_ID[0], input_ID[1], input_ID[2], input_ID[3], input_ID[4], input_ID[5]) ; }
		curren_time += 1;
		return 1;
    default :
      return 0;
  }
}




/*==========================================================================*/
/*  End of DriverModel.cpp                                                  */
/*==========================================================================*/
