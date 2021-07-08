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
            
            self.urbansim_file = self.setup['urbansim_file']
            self.gq_pop_file = self.setup['gq_pop_file']
            self.landarea_file = self.setup['landarea_file']
            self.blk_fct_file = self.setup['blk_fct_file']
            self.act_den_file = self.setup['act_den_file']

            self.smart_loc_file = self.setup['smart_loc_file']
            self.int_den_file = self.setup['int_den_file']

            self.blk_lut_file = self.setup['blk_lut_file']
            self.va_input_file = self.setup['va_input_file']
            self.usim_fields = self.setup['usim_fields']
            self.hhsize_fields = self.setup['hhsize_fields']
            self.numwrk_fields = self.setup['numwrk_fields']

        except Exception as err:
            msg = "Required setup parameter(s) were not found in file '" + setup_file + "'.\n" + str(err)
            raise RuntimeError(msg) from err

    #--------------------------------------------------------------------------------------------------

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
            msg = "Error reading SOV skim matrix " + self.sov_skim_file + ".\n" + str(err)
            raise RuntimeError(msg) from err

        #read the transit travel time matrix into an arr
        try:
            transit_file = omx.open_file(self.in_folder + "\\" + self.transit_skim_file, 'r')
            transit_mtx = transit_file[self.transit_skim_name]
            transit_arr = np.array(transit_mtx)
        except Exception as err:
            msg = "Error reading transit skim matrix " + self.transit_skim_file + ".\n" + str(err)
            raise RuntimeError(msg) from err
        
        #create a dataframe from the taz mapping keys, with the taz mapping values as the index
        taz_map_df = pd.DataFrame(taz_keys, index = taz_vals, columns = ['ID'])
        
        #read the employment data from a csv file
        #first column should be TAZ# and second column should be total employment
        try:
            infile = self.in_folder + "\\" + self.taz_emp_file
            emp_df = pd.read_csv(filepath_or_buffer=infile, header=0, index_col=None, usecols=[0,1])
        except Exception as err:
            msg = "Error reading input file " + self.taz_emp_file + " into dataframe.\n" + str(err)
            raise RuntimeError(msg) from err

        #Merge the taz map and employment dataframes on the taz column
        #performing an outer join and retaining each row from the taz map.
        #The resulting dataframe will contain employment counts for each TAZ present in the skim matrices.
        emp_df2 = pd.merge(taz_map_df, emp_df, how="left", left_on="ID", right_on=self.emp_cols[0])
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
            o_emp_df = pd.DataFrame(o_emp_arr4, columns=['ID', 'pctemp'+str(time)+'a'])
            #merge the dataframe into the emp_access_df dataframe
            emp_access_df = pd.merge(emp_access_df, o_emp_df, how="left", left_on="ID", right_on="ID")

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
            o_emp_df = pd.DataFrame(o_emp_arr4, columns=['ID', 'pctemp'+str(time)+'t'])
            #merge the dataframe into the emp_access_df dataframe
            emp_access_df = pd.merge(emp_access_df, o_emp_df, how="left", left_on="ID", right_on="ID")

        #rename the 'ID' column to 'taz'
        emp_access_df.rename(columns = {"ID":"taz"},
                             inplace = True)

        #write the employment accessibility metrics to a csv file
        out_file_path = self.out_folder + "\\" + self.emp_access_file
        emp_access_df.to_csv(path_or_buf=out_file_path, index = False)

    #-------------------------------------------------------------------------------------------------

    def activity_den_by_taz(self):
        #read the urbansim household data into a pandas dataframe. Use an iterator to filter on input
        try:
            infile = self.in_folder + "\\" + self.urbansim_file
            iter_csv = pd.read_csv(infile, iterator=True, chunksize=1000)
            df_usim = pd.concat([chunk[chunk['person_num']==1] for chunk in iter_csv])
            #get rid of unnecessary columns
            df_usim = df_usim[['block_id','persons']]
        except Exception as err:
            msg = "Error reading urbansim file " + self.urbansim_file + "into dataframe.\n" + str(err)
            raise RuntimeError(msg) from err

        #read the taz / block split lookup into a dataframe
        try:
            infile = self.in_folder + "\\" + self.blk_fct_file
            df_blk_taz_lut = pd.read_csv(filepath_or_buffer=infile, header=0, index_col=None)
            df_blk_taz_lut = df_blk_taz_lut[['block_id', 'taz', 'area_fct']]
        except Exception as err:
            msg = "Error reading block / taz lookup file " + self.blk_fct_file + "into dataframe.\n" + str(err)
            raise RuntimeError(msg) from err

        #Merge the urbansim and taz lookup dataframes and calculate household pop by taz
        df_usim = pd.merge(df_usim, df_blk_taz_lut, left_on="block_id", right_on="block_id")
        df_usim['hh_pop'] = df_usim['persons'] * df_usim['area_fct']
        df_usim = df_usim[['taz','hh_pop']]
        df_hh_pop_taz = df_usim.groupby('taz').sum()

        #read the group quarters population file into a dataframe
        try:
            infile = self.in_folder + "\\" + self.gq_pop_file
            df_gq_pop_taz = pd.read_csv(filepath_or_buffer=infile, header=0, index_col=None, usecols=[0,1])
            df_gq_pop_taz.columns = ['taz','gq_pop']
        except Exception as err:
            msg = "Error reading group quarters population file " + self.gq_pop_file + " into dataframe.\n" + str(err)
            raise RuntimeError(msg) from err
        
        #read the employment by taz file into a dataframe
        try:
            infile = self.in_folder + "\\" + self.taz_emp_file
            df_emp_taz = pd.read_csv(filepath_or_buffer=infile, header=0, index_col=None, usecols=[0,1])
            df_emp_taz.columns = ['taz','emp']
        except Exception as err:
            msg = "Error reading employment file " + self.taz_emp_file + " into dataframe.\n" + str(err)
            raise RuntimeError(msg) from err

        #read the land area by taz file into a dataframe
        try:
            infile = self.in_folder + "\\" + self.landarea_file
            df_area_taz = pd.read_csv(filepath_or_buffer=infile, header=0, index_col=None, usecols=[0,1])
            df_area_taz.columns = ['taz', 'land_area']
        except Exception as err:
            msg = "Error reading land area file " + self.landarea_file + " into dataframe.\n" + str(err)
            raise RuntimeError(msg) from err

        #merge the population, employment and land area dataframes
        df_act_den_taz = pd.merge(df_hh_pop_taz, df_gq_pop_taz, left_on="taz", right_on="taz")
        df_act_den_taz = pd.merge(df_act_den_taz, df_emp_taz, left_on="taz", right_on="taz")
        df_act_den_taz = pd.merge(df_act_den_taz, df_area_taz, left_on="taz", right_on="taz")
        df_act_den_taz["actden"] = \
            ((df_act_den_taz["hh_pop"] + df_act_den_taz["gq_pop"] + df_act_den_taz["emp"]) / 1000) / df_act_den_taz["land_area"]
        df_act_den_taz["jobpop"] = \
            df_act_den_taz.apply(lambda row: self.jp_bal(row['emp'], row['hh_pop'], row['gq_pop']), axis=1)
        
        #drop unnecessary columns
        df_act_den_taz = df_act_den_taz[['taz','actden','jobpop']]

        #write the activity density data to a csv file
        out_file_path = self.out_folder + "\\" + self.act_den_file
        df_act_den_taz.to_csv(path_or_buf=out_file_path, index = False)
    
    #-------------------------------------------------------------------------------------
    def jp_bal(self, emp, hhpop, gqpop):
        #calculate job / population balance metric
        if emp==0 and hhpop==0 and gqpop==0:
            jpb = 0
        else:
            jpb = 1 - (abs(emp - 0.2 * (hhpop + gqpop)) / (emp + 0.2 * (hhpop + gqpop)))

        return jpb

    #--------------------------------------------------------------------------------------------
    def int_den_by_bg(self):
        #read the EPA smart location data into a pandas dataframe
        try:
            infile = self.in_folder + "\\" + self.smart_loc_file
            #use a filter to grab only Massachusetts records
            iter_csv = pd.read_csv(infile, iterator=True, chunksize=1000, \
                                   usecols=['SFIPS','GEOID10','D3b','D3bao','D3bmm3','D3bmm4','D3bpo3','D3bpo4'])
            df_int_den_bg = pd.concat([chunk[chunk['SFIPS']==25] for chunk in iter_csv])
            
        except Exception as err:
            msg = "Error reading EPA smart location file " + self.smart_loc_file + " into dataframe.\n" + str(err)
            raise RuntimeError(msg) from err
        df_int_den_bg['intden'] = df_int_den_bg['D3bao'] + df_int_den_bg['D3bmm3'] + \
                                    df_int_den_bg['D3bmm4'] + df_int_den_bg['D3bpo3'] + df_int_den_bg['D3bpo4']
        df_int_den_bg['pct4way'] = df_int_den_bg['D3bmm4'] + df_int_den_bg['D3bpo4']

        #drop unnecessary columns and rename the block group id column to match UrbanSim
        df_int_den_bg = df_int_den_bg[['GEOID10','intden','pct4way']]
        df_int_den_bg.columns = ['blockgroup_id','intden','pct4way']

        #write the intersection density data to a csv file
        out_file_path = self.out_folder + "\\" + self.int_den_file
        df_int_den_bg.to_csv(path_or_buf=out_file_path, index = False)

    #--------------------------------------------------------------------------------------------------
    def assemble_va_inputs(self):
        #Assign a taz to UrbanSim households
        #Then merge selected UrbanSim fields with employment accessibility, activity density and employment
        #density data

        #read the UrbanSim data into a pandas dataframe
        try:
            infile = self.in_folder + "\\" + self.urbansim_file
            iter_csv = pd.read_csv(infile, iterator=True, chunksize=1000)
            df_usim = pd.concat([chunk[chunk['person_num']==1] for chunk in iter_csv])
            #slice off the desired columns
            df_usim = df_usim[self.usim_fields]
        except Exception as err:
            msg = "Error reading urbansim file " + self.urbansim_file + " into dataframe.\n" + str(err)
            raise RuntimeError(msg) from err

        #read the block / taz lookup into a dataframe
        try:
            infile = self.in_folder + "\\" + self.blk_lut_file
            blk_taz_lut = pd.read_csv(filepath_or_buffer=infile, header=0, index_col=None, usecols=['block_id','taz'])
        except Exception as err:
            msg = "Error reading taz lookup file " + infile + " into dataframe.\n" + str(err)
            raise RuntimeError(msg) from err

        #merge the block / taz lookup into the urbansim dataframe
        df_usim = pd.merge(df_usim, blk_taz_lut, how='left', left_on='block_id', right_on='block_id')

        #add and populate household size columns
        try:
            for i in range(len(self.hhsize_fields)):
                hhsiz_fld = self.hhsize_fields[i]
                #check to make sure at least one household has a person count of i+1
                #python is apparently unhappy when asked to run lambda functions on an empty dataframe
                if not(df_usim.loc[df_usim['persons'] == i+1].empty):
                    if i < len(self.hhsize_fields) - 1:
                        df_usim[hhsiz_fld] = df_usim.apply(lambda row: 1 if row.persons == i+1 else 0, axis = 1)
                    else:
                        df_usim[hhsiz_fld] = df_usim.apply(lambda row: 1 if row.persons >= i+1 else 0, axis = 1)
        except Exception as err:
            msg = "Error setting household size flags.\n" + str(err)
            raise RuntimeError(msg) from err

        #add and populate number of workers columns
        try:
            for i in range(len(self.numwrk_fields)):
                numwrk_fld = self.numwrk_fields[i]
                #check to see if at least one household has a worker count of i
                if not(df_usim.loc[df_usim['workers'] == i].empty):
                    if i < len(self.numwrk_fields) - 1:
                        df_usim[numwrk_fld] = df_usim.apply(lambda row: 1 if row.workers == i else 0, axis = 1)
                    else:
                        df_usim[numwrk_fld] = df_usim.apply(lambda row: 1 if row.workers >= i else 0, axis = 1)
        except Exception as err:
            msg = "Error setting worker count fields.\n" + str(err)
            raise RuntimeError(msg) from err

        #dummy variable for low income households
        try:
            df_usim['dum_income'] = df_usim.apply(lambda row: 1 if row.hh_inc < 35000 else 0, axis = 1)
        except Exception as err:
            msg = "Error setting hh income dummy variable.\n" + str(err)
            raise RuntimeError(msg) from err

        #merge the intersection density data into the urbansim dataframe
        try:
            infile = self.in_folder + "\\" + self.int_den_file
            df_intden = pd.read_csv(filepath_or_buffer=infile, header=0, index_col=None)
        except Exception as err:
            msg = "error reading intersection density file.\n" + str(err)
            raise RuntimeError(msg) from err

        df_usim = pd.merge(df_usim, df_intden, how='left', left_on='blockgroup_id', right_on='blockgroup_id')
        
        #merge the employment accessibility data into the urbansim dataframe
        try:
            infile = self.in_folder + "\\" + self.emp_access_file
            df_empden = pd.read_csv(filepath_or_buffer=infile, header=0, index_col=None)
        except Exception as err:
            msg = "error reading employment accessibility file.\n" + str(err)
            raise RuntimeError(msg) from err

        try:
            df_usim = pd.merge(df_usim, df_empden, how='right', left_on='taz', right_on='taz')
            #drop the ID column
            df_usim.drop('ID')
        except KeyError:
            #ignore error if column didn't exist
            pass
        except Exception as err:
            msg = "error merging empden into urbansim dataframe.\n" + str(err)
            raise RuntimeError(msg) from err

        #merge the activity density data into the urbansim dataframe
         #merge the employment accessibility data into the urbansim dataframe
        try:
            infile = self.in_folder + "\\" + self.act_den_file
            df_actden = pd.read_csv(filepath_or_buffer=infile, header=0, index_col=None)
        except Exception as err:
            msg = "error reading activity density file.\n" + str(err)
            raise RuntimeError(msg) from err

        df_usim = pd.merge(df_usim, df_actden, how='left', left_on='taz', right_on='taz')

        #write the va model input data to a csv file
        #write the intersection density data to a csv file
        out_file_path = self.out_folder + "\\" + self.va_input_file
        df_usim.to_csv(path_or_buf=out_file_path, index = False)
