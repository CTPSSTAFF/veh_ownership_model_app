import pandas as pd
import numpy as np
import yaml
import os

class veh_model:
    """
    A base class defining functionality common to any vehicle ownership model being applied.
    Also provides placeholder methods for functionality that should be defined in subclasses
    that implement specific model types.

    Args:
        setup_file (str): name of YAML file listing the folder path of the working directory,
        names of input and output files,the name of the model specification file,
        lists of required fields for output files and the name of the model specification yaml file 
    """

    def __init__(self,
                 setup_file: str):
        try:
            with open(setup_file, 'r') as stream:    
                setup = yaml.load(stream, Loader=yaml.FullLoader)
        except Exception as err:
            msg = "Error reading setup file (" + setup_file + ")."
            print(msg)
            raise RuntimeError(msg) from err
        
        self.setup = setup if setup is not None else {}

        try:
            self.working_dir = self.setup['working_dir']
            self.data_path = self.setup['data_file_path']
            self.input_file = self.setup['input_data_file']
            self.output_file = self.setup['output_disagg_file']
            self.aggregate = self.setup['aggregate']
            if self.aggregate == "yes":
                self.output_agg_file = self.setup['output_agg_file']
                self.agg_fields = self.setup['output_agg_fields']
            self.model_spec_file = self.setup['model_spec_file']
            self.veh_fields = self.setup['veh_fields']
        except Exception as err:
            msg = "Required setup parameter(s) were not found in file '" + setup_file + "."
            print(msg)
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
        try:
            outfilepath = self.data_path + "\\" + self.output_file
            self.df.to_csv(path_or_buf=outfilepath,index=False)
        except Exception as err:
            msg = "Error writing dataframe to file."
            raise RuntimeError(msg) from err

