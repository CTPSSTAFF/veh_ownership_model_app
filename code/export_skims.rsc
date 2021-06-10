Macro "export_skims"


    on error do
        err_msg = GetLastError({"Reference Info": true})
        ShowMessage("Veh_Model_Test: " + err_msg)
        ok = 0
        goto quit
    end

    //When VA model execution is incorporated within the flow chart model execution, 
    //these variables should be included in the model argmuments list
    input_folder = "D:\\Projects\\Exploratory_Modelling\\Inputs\\Databases\\"
    skim_folder = "D:\\Projects\\Exploratory_Modelling\\scenarios\\Scen_00\\Out\\"
    out_folder = "D:\\Projects\\veh_ownership_model_app\test_data\\"
    taz_db = input_folder + "Statewide_TAZs_2017.dbd"
    am_sov_skim_mtx = skim_folder + "AM\\SOV_skim.mtx"
    pm_sov_skim_mtx = skim_folder + "PM\\SOV_skim.mtx"
    am_transit_skim_mtx = skim_folder + "AM\\wat_for_all_tr_skim.mtx"
    pm_transit_skim_mtx = skim_folder + "PM\\wat_for_all_tr_skim.mtx"
    tmp_sov_mtx = out_folder + "sov_time.mtx"
    tmp_transit_mtx = out_folder + "transit_time.mtx"
    out_sov_skim_mtx = out_folder + "sov_skim.omx"
    out_transit_skim_mtx = out_folder + "transit_skim.omx"

    //find the MAPC TAZs
    lyrs = RunMacro("TCB Add DB Layers", taz_db)
    taz_lyr = lyrs[1]
    SetView(taz_lyr)
    n = SelectByQuery("mapcZ", "Several", "Select * where RPA = 'MAPC'",)

    sov_am_mtx = OpenMatrix(am_sov_skim_mtx,)
    sov_pm_mtx = OpenMatrix(pm_sov_skim_mtx,)
    transit_am_mtx = OpenMatrix(am_transit_skim_mtx,)
    transit_pm_mtx = OpenMatrix(pm_transit_skim_mtx,)

    mapc_idx = CreateMatrixIndex("mapcZ", sov_am_mtx, "Both", taz_lyr+"|mapcZ", "ID", "ID",)
    mapc_idx = CreateMatrixIndex("mapcZ", sov_pm_mtx, "Both", taz_lyr+"|mapcZ", "ID", "ID",)
    mapc_idx = CreateMatrixIndex("mapcZ", transit_am_mtx, "Both", taz_lyr+"|mapcZ", "ID", "ID",)
    mapc_idx = CreateMatrixIndex("mapcZ", transit_pm_mtx, "Both", taz_lyr+"|mapcZ", "ID", "ID",)
    
    sov_am_mc = CreateMatrixCurrency(sov_am_mtx, "CongTime", "mapcZ", "mapcZ",)
    sov_pm_mc = CreateMatrixCurrency(sov_pm_mtx, "CongTime", "mapcZ", "mapcZ",)
    transit_am_mc = CreateMatrixCurrency(transit_am_mtx, "Total_Time", "mapcZ", "mapcZ",)
    transit_pm_mc = CreateMatrixCurrency(transit_pm_mtx, "Total_Time", "mapcZ", "mapcZ",)

    //Calculate average sov congested time by add, cell by cell, the am and pm matrix currencies
    //and dividing the result by 2

    MatrixCellbyCell(sov_am_mc, sov_pm_mc, {
        {"File Name", tmp_sov_mtx},
        {"Label", "SOV congested time"},
        {"Type", "Float"},
        {"Sparse", "No"},
        {"Column Major", "No"},
        {"File Based", "Yes"},
        {"Force Missing", "No"},
        {"Operator", 3}, //addition
        {"Scale Left", 0.5}, 
        {"Scale Right", 0.5}, //'scale left' and 'scale right' let us calculate an average
    })

    //Repeat the procedure to calcultate average transit travel times

    MatrixCellbyCell(transit_am_mc, transit_pm_mc, {
        {"File Name", tmp_transit_mtx},
        {"Label", "SOV congested time"},
        {"Type", "Float"},
        {"Sparse", "No"},
        {"Column Major", "No"},
        {"File Based", "Yes"},
        {"Force Missing", "No"},
        {"Operator", 3}, //addition
        {"Scale Left", 0.5}, 
        {"Scale Right", 0.5}, //'scale left' and 'scale right' let us calculate an average
    })

    //save the average travel time matrices to OpenMatrix files
    sov_mtx = OpenMatrix(tmp_sov_mtx,)
    sov_mc = CreateMatrixCurrency(sov_mtx, "SOV_cong_time", "mapcZ", "mapcZ",)
    sov_omx = CopyMatrix(sov_mc, {
        {"File Name", out_sov_skim_mtx},
        {"Label", "CongTime"},
        {"File Based", "Yes"}
    })

    transit_mtx = OpenMatrix(tm_transit_mtx,)
    tranxit_mc = CreateMatrixCurrency(transit_mtx, "Transit_Total_Time", "mapcZ", "mapcZ",)
    transit_omx = CopyMatrix(transit_mc, {
        {"File Name", out_transit_skim_mtx},
        {"Label", "TotalTime"},
        {"File Based", "Yes"}
    })

    //delete the temporary files
    DeleteFile(tmp_sov_mtx)
    DeleteFile(tmp_transit_mtx)

    ok = 1
    quit:
    return(ok)

endMacro