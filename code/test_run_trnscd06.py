from poisson_veh_model import poisson_model
from time import localtime, strftime

try:
    print("Start: " + strftime("%H:%M:%S", localtime()))
    
    my_model = poisson_model("D:\\Projects\\veh_ownership_model_app\\code\\utah_poisson_setup_trnscd06.yml")

    print("Loading data: " + strftime("%H:%M:%S", localtime()))

    my_model.load_data()

    print("Running model: " + strftime("%H:%M:%S", localtime()))

    my_model.run_model()

    print("Saving disaggregate data: " + strftime("%H:%M:%S", localtime()))

    my_model.save_results()

    if my_model.aggregate:
        print("Aggregating results: " + strftime("%H:%M:%S", localtime()))
        my_model.aggregate_results()

    print("End: " + strftime("%H:%M:%S", localtime()))

except Exception as err:
    print(err)