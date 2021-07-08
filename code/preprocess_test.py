from va_preprocessors import va_preprocess
from time import localtime, strftime

try:
    print("Start pre-processor: " + strftime("%H:%M:%S", localtime()))
    preprocess = va_preprocess("D:\\Projects\\veh_ownership_model_app\\code\\va_setup_2020.yml")

    print("Calculating employment accessibility: " + strftime("%H:%M:%S", localtime()))
    preprocess.emp_accessibility_by_taz()

    print("Calculating activity density: " + strftime("%H:%M:%S", localtime()))
    preprocess.activity_den_by_taz()

    print("Calculating intersection density: " + strftime("%H:%M:%S", localtime()))
    preprocess.int_den_by_bg()

    print("Assembling VA model inputs: " + strftime("%H:%M:%S", localtime()))
    preprocess.assemble_va_inputs()

    print("End pre-processor: " + strftime("%H:%M:%S", localtime()))

except Exception as err:
    print(err)


                           
