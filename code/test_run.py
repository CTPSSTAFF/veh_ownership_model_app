from poisson_veh_model import poisson_model

my_model = poisson_model("utah_poisson_setup.yml")

print(my_model.working_dir)
print(my_model.coeffs)
