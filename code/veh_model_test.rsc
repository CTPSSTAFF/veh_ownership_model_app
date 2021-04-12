Macro "Veh_Model_Test"

    on error do
        err_msg = GetLastError({"Reference Info": true})
        ShowMessage("Veh_Model_Test: " + err_msg)
        ok = 0
        goto quit
    end

    RunProgram("G:\\Regional_Modeling\\veh_ownership_model_app\\code\\test_run.bat", {})
    Pause(5000)

    ShowMessage("Done!")
    ok = 1
    quit:
    return(ok)
endMacro