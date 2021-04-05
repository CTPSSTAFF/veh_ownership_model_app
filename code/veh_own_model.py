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
            msg = "Error reading setup file (" + setup_file + ")\n" + err.message
            print(msg)
            raise
        
        self.setup = setup if setup is not None else {}

        try:
            self.working_dir = self.setup['working_dir']
            self.input_file = self.setup['input_data_file']
            self.output_file = self.setup['output_disagg_file']
            self.aggregate = self.setup['aggregate']
            if self.aggregate == "yes":
                self.output_agg_file = self.setup['output_agg_file']
                self.agg_fields = self.setup['output_agg_fields']
            self.model_spec_file = self.setup['model_spec_file']
            self.veh_fields = self.setup['veh_fields']
        except Exception as err:
            msg = "Required setup parameter(s) were not found in file '" + setup_file + "'\n" + err.message
            print(msg)
            raise

    # Method load_data should be defined by sublclasses of veh_model
    # The base class method functionality is limited to printing a message to this effec.
    # This message will only be printed if the developer of the sublcass failed to define the method there
    def load_data(self):
        msg = "Method load_data is undefined."
        raise RuntimeError(msg)