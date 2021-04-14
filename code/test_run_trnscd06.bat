rem test_run.bat
rem
rem activate conda environment va_model
rem then run python script test_run.python

rem redwagon
rem c:\users\paul\AppData\Local\Continuum\anaconda3\condabin\activate va_model && python test_run.py

rem trnscd06
c:\ProgramData\Anaconda3\condabin\activate va_model && python D:\Projects\veh_ownership_model_app\code\test_run_trnscd06.py & timeout /t 30
