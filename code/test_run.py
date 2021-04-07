from poisson_veh_model import poisson_model

try:
    my_model = poisson_model("utah_poisson_setup.yml")

    #print(my_model.working_dir)
    #print(my_model.coeffs)

    my_model.load_data()

    my_model.run_model()

except Exception as err:
    print(err)
