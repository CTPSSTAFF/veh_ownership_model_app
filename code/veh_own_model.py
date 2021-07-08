import pandas as pd
import yaml
import os

class VehModel:
    """
    A base class defining functionality common to any vehicle ownership model being applied.
    Also provides placeholder methods for functionality that should be defined in subclasses
    that implement specific model types.

    Args:
        setup_file (str): name of YAML file listing the folder path of the code directory,
        names of input and output files,the name of the model specification file,
        lists of required fields for output files and the name of the model specification yaml file 
    """

    def __init__(self,
                 setup_file: str):
        try:
            with open(setup_file, 'r') as stream:    
                setup = yaml.load(stream, Loader=yaml.FullLoader)
        except Exception as err:
            msg = "Error reading setup file (" + setup_file + ").\n" + str(err)
            raise RuntimeError(msg) from err
        
        self.setup = setup if setup is not None else {}

        try:
            self.code_path      = self.setup['code_path']
            self.data_path      = self.setup['data_file_path']
            self.input_file     = self.setup['input_data_file']
            self.output_file    = self.setup['output_disagg_file']
            self.aggregate      = self.setup['aggregate']
            if self.aggregate:
                self.output_agg_file = self.setup['output_agg_file']
                self.agg_fields      = self.setup['output_agg_fields']
            self.model_spec_file = self.code_path + "\\" + self.setup['model_spec_file']
            self.veh_fields      = self.setup['veh_fields']
            self.blk_fct_file   = self.setup['blk_fct_file']
            self.split_factor   = self.setup['split_factor']
            
        except Exception as err:
            msg = "Required setup parameter(s) were not found in file '" + setup_file + ".\n" + str(err)
            raise RuntimeError(msg) from err

    # Method load_data should be defined by subclasses of veh_model
    # The base class method functionality is limited to raising a NotImplementedError with a helpful message
    # and will only be executed if the developer of the sublcass failed to define the method there.
    # When implemented, the method should read the input data file specified in the setup file into a pandas dataframe
    def load_data(self):
        msg = "Error: Method load_data is undefined."
        raise NotImplementedError(msg)

    # Method run_model should be defined by subclasses of veh_model
    # The base class method functionality is limited to raising a NotImplementedError with a helpful message
    # and will only be executed if the developer of the sublcass failed to define the method there.
    # When implemented, the method will apply the coefficients in the model specification file to their corresponding
    # columns in the dataframe created by the load_data method, adding columns to store the predicted vehicle counts.
    def run_model(self):
        msg = "Error: Method run_model is undefined."
        raise NotImplementedError(msg)

    # Method save_results
    # write dataframe of processed household / zonal data to a csv file
    def save_results(self):
        #print("writing dataframe to file...")
        try:
            out_file_path = self.data_path + "\\" + self.output_file
            self.df.to_csv(path_or_buf=out_file_path,index=False)
        except Exception as err:
            msg = "Error writing dataframe to file.\n" + str(err)
            raise RuntimeError(msg) from err

    # Method split_hh_to_taz
    # Merge disaggregate model results dataframe with block to taz split table
    # Apply split factors to 0 / 1 flag columns
    def split_hh_to_taz(self):
        #read block / taz factor file into a dataframe
        try:
            infile = self.data_path + "\\" + self.blk_fct_file
            df_factors = pd.read_csv(filepath_or_buffer=infile, header=0, index_col=None, usecols=['block_id','area_fct'])
        except Exception as err:
            msg = "Error reading block split factor file\n" + str(err)
            raise RuntimeError(msg) from err

        #drop taz column from VA model output
        try:
            self.df.drop('taz')
        except KeyError:
            #no big deal if the column doesn't exist
            pass
        except Exception as err:
            msg = "Error dropping taz column.\n" + str(err)
            raise RuntimeError(msg) from err

        #merge the split factors into the va output
        self.df = pd.merge(self.df, df_factors, left_on='block_id', right_on='block_id')

        #apply the split factors to the flags
        for i in range(1,len(self.agg_fields)):
            self.df[self.agg_fields[i]] = self.df[self.agg_fields[i]] * self.df[self.split_factor]
 
    # Method aggregate_results
    # Summarize dataframe of processed household / zonal data by aggregate geography
    # Include fields in output_agg_fields list
    def aggregate_results(self):
        #print("aggregating results...")
        try:
            df2         = self.df[self.agg_fields]
            df2_grouped = df2.groupby(self.agg_fields[0]).sum()
            #round all values to integers
            for i in range(1,len(self.agg_fields)):
                df2_grouped[self.agg_fields[i]] = round(df2_grouped[self.agg_fields[i]],0)
        except Exception as err:
            msg = "Error aggregating results.\n" + str(err)
            raise RuntimeError(msg) from err

        #write the results to a text file
        try:
            out_file_path = self.data_path + "\\" + self.output_agg_file
            df2_grouped.to_csv(path_or_buf=out_file_path)
        except Exception as err:
            msg = "Error writing aggregated output to file.\n" + str(err)
            raise RuntimeError(msg) from err
