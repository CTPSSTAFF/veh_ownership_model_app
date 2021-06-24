rem test_run.bat
rem
rem activate conda environment va_model
rem then run python script test_run.python

rem redwagon
rem c:\users\paul\AppData\Local\Continuum\anaconda3\condabin\activate va_model && python test_run.py

rem trnscd06
rem In order to execute this script from a TransCAD macro, the full path to the Python script must be specified
c:\ProgramData\Anaconda3\condabin\activate va_model && python D:\Projects\veh_ownership_model_app\code\preprocess_and_run_test.py & timeout /t 15