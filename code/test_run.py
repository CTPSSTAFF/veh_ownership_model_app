from poisson_veh_model import poisson_model

try:
    my_model = poisson_model("utah_poisson_setup.yml")

    my_model.load_data()

    my_model.run_model()

    my_model.save_results()

except Exception as err:
    print(err)
