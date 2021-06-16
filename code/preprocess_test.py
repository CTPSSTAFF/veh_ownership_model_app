from va_preprocessors import va_preprocess

try:
    preprocess = va_preprocess("D:\\Projects\\veh_ownership_model_app\\code\\va_setup.yml")
    preprocess.emp_accessibility_by_taz()

except Exception as err:
    print(err)


                           
