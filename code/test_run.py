from poisson_veh_model import PoissonModel
from time import localtime, strftime

try:
    print("Start: " + strftime("%H:%M:%S", localtime()))
    
    #Note: in order to execute model application from a TransCAD macro, the full path to the setup file must be specified
    my_model = PoissonModel("D:\\Projects\\veh_ownership_model_app\\code\\utah_poisson_setup.yml")

    print("Loading data: " + strftime("%H:%M:%S", localtime()))

    my_model.load_data()

    print("Running model: " + strftime("%H:%M:%S", localtime()))

    my_model.run_model()

    print("Factoring block data to taz: " + strftime("%H:%M:%S", localtime()))

    my_model.split_hh_to_taz()

    print("Saving disaggregate data: " + strftime("%H:%M:%S", localtime()))

    my_model.save_results()

    if my_model.aggregate:
        print("Aggregating results: " + strftime("%H:%M:%S", localtime()))
        my_model.aggregate_results()

    print("End: " + strftime("%H:%M:%S", localtime()))

except Exception as err:
    print(err)
