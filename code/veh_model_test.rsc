Macro "Veh_Model_Test"

    on error do
        err_msg = GetLastError({"Reference Info": true})
        ShowMessage("Veh_Model_Test: " + err_msg)
        ret = -1
        ok = 0
        goto quit
    end

    ret = RunProgram("D:\\Projects\\veh_ownership_model_app\\code\\test_run_trnscd06.bat", {{"Maximize", "True"}})
    Pause(1000)

    ShowMessage("VA model application completed with return code = " + i2s(ret) + ".")
    ok = 1
    quit:
    return(ok)
endMacro