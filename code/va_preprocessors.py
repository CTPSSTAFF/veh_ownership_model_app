import openmatrix as omx
import pandas as pd
import numpy as np
import os
import yaml

class va_preprocess:
    """
    Implementing the pre- and postprocessing functions in classes
    provides the benefit of parsing the yaml file just once, storing input and
    output folders and file names in instance variables

    Args:
        setup file (str): name of YAML file listing the folder paths, file
        names and other settings
    """

    def __init__(self,
                 setup_file: str):

        try:
            with open(setup_file, 'r') as stream:
                setup = yaml.load(stream, Loader= yaml.FullLoader)
        except Exception as err:
            msg = "Error reading setup file (" + setup_file + ")."
            print(msg)
            raise RuntimeError(msg) from err

        self.setup = setup if setup is not None else {}

        try:
            self.in_folder = self.setup['in_folder']
            self.out_folder = self.setup['out_folder']

            self.sov_skim_file = self.setup['sov_skim_file']
            self.transit_skim_file = self.setup['transit_skim_file']
            self.taz_emp_file = self.setup['taz_emp_file']
            self.emp_cols = self.setup['emp_cols']
            self.emp_access_file = self.setup['emp_access_file']
            self.sov_times = self.setup['sov_times']
            self.sov_skim_name = self.setup['sov_skim_name']
            self.transit_times = self.setup['transit_times']
            self.transit_skim_name = self.setup['transit_skim_name']
            self.skim_index = self.setup['skim_index']
            
        except Exception as err:
            msg = "Required setup parameter(s) were not found in file '" + setup_file + "'."
            raise RuntimeError(msg) from err

    def emp_accessibility_by_taz(self):
        #read the sov congested time matrix into an array
        try:
            sov_file = omx.open_file(self.in_folder + "\\" + self.sov_skim_file, 'r')
            sov_mtx = sov_file[self.sov_skim_name]
            sov_arr = np.array(sov_mtx)

            #capture the zone mappings in a dict
            taz_map = sov_file.mapping(self.skim_index)
            taz_keys = list(taz_map.keys())
            taz_vals = list(taz_map.values())
            
        except Exception as err:
            msg = "Error reading SOV skim matrix " + self.sov_skim_file + "."
            print(msg)
            raise RuntimeError(msg) from err

        #read the transit travel time matrix into an arr
        try:
            transit_file = omx.open_file(self.in_folder + "\\" + self.transit_skim_file, 'r')
            transit_mtx = transit_file[self.transit_skim_name]
            transit_arr = np.array(transit_mtx)
        except Exception as err:
            msg = "Error reading transit skim matrix " + self.transit_skim_file + "."
            print(msg)
            raise RuntimeError(msg) from err
        
        #create a dataframe from the taz mapping keys, with the taz mapping values as the index
        taz_map_df = pd.DataFrame(taz_keys, index = taz_vals, columns = ['ID'])
        
        #read the employment data from a csv file
        #first column should be TAZ# and second column should be total employment
        try:
            infile = self.in_folder + "\\" + self.taz_emp_file
            emp_df = pd.read_csv(filepath_or_buffer=infile, header=0, index_col=None, usecols=[0,1])
        except Exception as err:
            msg = "Error reading input file " + self.taz_emp_file + " into dataframe."
            print(msg)
            raise RuntimeError(msg) from err

        #Merge the taz map and employment dataframes on the taz column
        #performing an outer join and retaining each row from the taz map.
        #The resulting dataframe will contain employment counts for each TAZ present in the skim matrices.
        emp_df2 = pd.merge(taz_map_df, emp_df, how="left", on=["ID",self.emp_cols[0]])
        #drop the TAZ column from the dataframe
        emp_df2 = emp_df2[self.emp_cols[1]]

        #convert the employmment dataframe to a numpy array
        emp_arr = emp_df2.to_numpy()

        #calculate regional employment as the sum of the employment array
        tot_emp = np.sum(emp_arr)
        #print(tot_emp)

        #initialize the output dataframe as a copy of the taz mapping keys dataframe
        emp_access_df = taz_map_df
        
        #iterate over the sov travel time thresholds
        for time in self.sov_times:
            #create an array of 0/1 flags based on whether o-d travel time is within threshold
            flag_arr = np.where(sov_arr==0,0,(np.where(sov_arr<=time,1,0)))
            #multiply the flags by the destination zone employment
            #we need to transpose the flag array first, then transpose the result
            od_emp_arr = ((flag_arr.T) * emp_arr).T
            #sum the employment within the travel time threshold by origin zone
            o_emp_arr = np.sum(od_emp_arr,0)
            #calculate the percentage of regional employment within travel time threshold
            o_emp_arr2 = o_emp_arr / tot_emp            
            #add the TAZ #s to the array of employment within time threshold by origin taz
            o_emp_arr3 = np.array([taz_keys,o_emp_arr2])
            #transpose the array
            o_emp_arr4 = o_emp_arr3.T
            #convert the array to a dataframe
            o_emp_df = pd.DataFrame(o_emp_arr4, columns=['ID', 'sov_pct'+str(time)])
            #merge the dataframe into the emp_access_df dataframe
            emp_access_df = pd.merge(emp_access_df, o_emp_df, how="left", on=["ID","ID"])

        #iterate over the transit travel time thresholds
        for time in self.transit_times:
            #create an array of 0/1 flags based on whether o-d travel time is within threshold
            flag_arr = np.where(transit_arr==0,0,(np.where(transit_arr<=time,1,0)))
            #multiply the flags by the destination zone employment
            #we need to transpose the flag array first, then transpose the result
            od_emp_arr = ((flag_arr.T) * emp_arr).T
            #sum the employment within the travel time threshold by origin zone
            o_emp_arr = np.sum(od_emp_arr,0)
            #calculate the percentage of regional employment within travel time threshold
            o_emp_arr2 = o_emp_arr / tot_emp           
            #add the TAZ #s to the array of employment within time threshold by origin taz
            o_emp_arr3 = np.array([taz_keys,o_emp_arr2])
            #transpose the array
            o_emp_arr4 = o_emp_arr3.T
            #convert the array to a dataframe
            o_emp_df = pd.DataFrame(o_emp_arr4, columns=['ID', 'transit_pct'+str(time)])
            #merge the dataframe into the emp_access_df dataframe
            emp_access_df = pd.merge(emp_access_df, o_emp_df, how="left", on=["ID","ID"])

        #write the employment accessibility metrics to a csv file
        out_file_path = self.out_folder + "\\" + self.emp_access_file
        emp_access_df.to_csv(path_or_buf=out_file_path, index = False)
            
        
            
            

        

        


        
        

    
        

