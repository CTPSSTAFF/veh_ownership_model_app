from va_preprocessors import va_preprocess
from poisson_veh_model import PoissonModel
from time import localtime, strftime

try:
    print("Start pre-processor: " + strftime("%H:%M:%S", localtime()))
    preprocess = va_preprocess("D:\\Projects\\veh_ownership_model_app\\code\\va_setup.yml")

    print("Calculating employment accessibility: " + strftime("%H:%M:%S", localtime()))
    preprocess.emp_accessibility_by_taz()

    print("Calculating activity density: " + strftime("%H:%M:%S", localtime()))
    preprocess.activity_den_by_taz()

    print("Calculating intersection density: " + strftime("%H:%M:%S", localtime()))
    preprocess.int_den_by_bg()

    print("Assembling VA model inputs: " + strftime("%H:%M:%S", localtime()))
    preprocess.assemble_va_inputs()
    
    print("Start model: " + strftime("%H:%M:%S", localtime()))
    
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

    print("End model: " + strftime("%H:%M:%S", localtime()))

except Exception as err:
    print(err)
