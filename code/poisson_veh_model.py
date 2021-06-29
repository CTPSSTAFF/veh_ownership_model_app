import pandas as pd
import yaml
import os
import math
from veh_own_model import VehModel

class PoissonModel(VehModel):
    """
    Defines an implementation of a poisson count model for estimating household vehicles

    Args:
        setup (str): name of YAML file listing the folder path of the working directory,
        names of input and output files,the name of the model specification file,
        lists of required fields for output files and the name of the model specification yaml file
    """

    def __init__(self,
                 setup_file):
        #print("initializing...")
        super().__init__(setup_file=setup_file)

        #parse the model specification file
        try:
            with open(self.model_spec_file, 'r') as stream:
                self.specs = yaml.load(stream, Loader=yaml.FullLoader)
        except Exception as err:
            msg = "Error reading model specification file (" + self.model_spec_file + ").\n" + str(err)
            raise RuntimeError(msg) from err

        try:
            self.field_map = self.specs['field_map']
            self.coeffs    = self.specs['coeffs']
        except Exception as err:
            msg = "Required model specification parameter(s) were not found in file '" + self.model_spec_file + "'.\n" + str(err)
            raise RuntimeError(msg) from err

    # method load_data:
    # read input data file into a pandas dataframe
    # verify that required model inputs are present in the dataframe
    # test1: keep just the first 1000 rows
    def load_data(self):
        #read the csv file into a dataframe and capture the column names in a list
        #print("loading input data...")
        try:
            infile  = self.data_path + "\\" + self.input_file
            self.df = pd.read_csv(infile)
            cols    = self.df.columns
            self.df = self.df.fillna(0)
        except Exception as err:
            msg = "Error reading input file " + self.input_file + " into dataframe.\n" + str(err)
            raise RuntimeError(msg) from err

        #ensure that all model coefficients map to columns in the input dataframe
        #the first dependent variable is the intercept / constant - ignore it

        keys = list(self.coeffs.keys())

        #require that first coefficient is named 'intercept'
        #then test here to make sure it exists
        for i in range (1,len(self.coeffs)):
            key = keys[i]
            if len(self.field_map) == 0:
                #field map is empty: the column names and coefficient names should be equivalent
                if key not in cols:
                    msg = "Coefficient '" + key + "' is not associated with a column in " + self.input_file + ".\n"
                    raise RuntimeError(msg)
            else:
                #get the column name associated with the coefficient from the field map
                try:
                    col  = self.field_map[key]
                except Exception as err:
                    msg = "Key '"  + key + "' not found in field map.\n" + str(err)
                    raise RuntimeError(msg) from err

                if col not in cols:
                    msg = "Coefficient '" + key + "' is not associated with a column in " + self.input_file + ".\n" 
                    raise RuntimeError(msg)

    # method run_model:
    # add a column named 'log_veh' to the dataframe created by the load_data method
    # populate the new column by applying the coefficients in the model spec to the appropriate columns
    def run_model(self):

        try:
            #convert the coefficient keys from a dictionary view to a list so that we can reference them by position
            coeff_names = list(self.coeffs.keys())

            #set the log of the vehicle count equal to the first coefficient, which should be the intercept
            int_term = coeff_names[0]
            self.df['log_veh'] = self.coeffs[int_term]
        except Exception as err:
            #failure here is most likely because the load_data method has not been run and the dataframe doesn't exist
            msg = "Unable to add a column to the input dataframe. Confirm that the load_data method is being executed before run_model.\n" + str(err)
            raise RuntimeError(msg) from err

        #iterate over the remaining coefficients
        #add the product of the coefficient and its corresponding column value to the log of the vehicle count
        try:
            for i in range (1, len(coeff_names)):
                coeff_name = coeff_names[i]
                #if the field_map is empty, the data column names and coefficient names should match
                if len(self.field_map) == 0:
                    col_name = coeff_name
                else:
                    col_name = self.field_map[coeff_name]
                
                self.df['log_veh'] = self.df['log_veh'] + self.df[col_name] * self.coeffs[coeff_name]

            #calculate the predicted household vehicle count
            self.df['vehicles'] = self.df.apply(lambda row: int(round(math.exp(row.log_veh),0)), axis=1)
        except Exception as err:
            msg = "Error applying model coefficients.\n" + str(err)
            raise RuntimeError(msg) from err

        #set the household vehicle flags
        try:
            for i in range(len(self.veh_fields)):
                veh_fld = self.veh_fields[i]

                #initialize new column to zero
                self.df[veh_fld] = 0

                #check to make sure at least one household has a vehicle count of i
                #python is apparently unhappy when asked to run lambda functions on an empty dataframe
                if not(self.df.loc[self.df['vehicles'] == i].empty):
                    if i < len(self.veh_fields) - 1:
                        self.df[veh_fld] = self.df.apply(lambda row: 1 if row.vehicles == i else 0, axis=1)
                    else:
                        self.df[veh_fld] = self.df.apply(lambda row: 1 if row.vehicles >= i else 0, axis=1)
        except Exception as err:
            msg = "Error setting household vehicle flags.\n" + str(err)
            raise RuntimeError(msg) from err
