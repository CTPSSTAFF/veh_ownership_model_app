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
            err.message = "Error reading setup file (" + setup_file + ")\n" + err.message
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
            err.message = "Required setup parameter(s) not found in file '" + setup_file + "'\n" + err.message
            raise
