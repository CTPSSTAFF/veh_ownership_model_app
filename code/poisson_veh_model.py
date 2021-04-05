import pandas as pd
import numpy as np
import yaml
import os
from veh_own_model import veh_model

class poisson_model(veh_model):
    """
    Defines an implementation of a poisson count model for estimating household vehicles

    Args:
        setup (str): name of YAML file listing the folder path of the working directory,
        names of input and output files,the name of the model specification file,
        lists of required fields for output files and the name of the model specification yaml file
    """

    def __init__(self,
                 setup_file):
        super().__init__(setup_file=setup_file)

        #parse the model specification file
        try:
            with open(self.model_spec_file, 'r') as stream:
                specs = yaml.load(stream, Loader=yaml.FullLoader)
        except Exception as err:
            msg = "Error reading model specification file (" + self.model_spec_file + ")\n" + err.message
            print(msg)
            raise

        self.specs = specs if specs is not None else {}

        try:
            self.field_map = self.specs['field_map']
            self.coeffs = self.specs['coeffs']
        except Exception as err:
            msg = "Required model specification parameter(s) were not found in file '" + self.model_spec_file + "'\n" + err.message
            print(msg)
            raise

    # method load_data:
    # read input data file into a pandas dataframe
    # verify that required model inputs are present in the dataframe
    # test1: keep just the first 1000 rows
    def load_data(self):
        infile = self.data_path + "\\" + self.input_file
        df = pd.read_csv(infile)[0:1000]
        print(df.describe())
        print(df.head())
        print(df.columns)

        
        
                
