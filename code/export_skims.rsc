Macro "export_skims"

    on error do
        err_msg = GetLastError({"Reference Info": true})
        ShowMessage("Veh_Model_Test: " + err_msg)
        ok = 0
        goto quit
    end

    ret = RunMacro("TCB Init")

    //When VA model execution is incorporated within the flow chart model execution, 
    //these variables should be included in the model argmuments list
    input_folder = "D:\\Projects\\Exploratory_Modelling\\Inputs\\Databases\\"
    skim_folder = "D:\\Projects\\Exploratory_Modelling\\scenarios\\Scen_00\\Out\\"
    out_folder = "D:\\Projects\\veh_ownership_model_app\\test_data\\"
    taz_db = input_folder + "Statewide_TAZs_2017.dbd"
    am_sov_skim_mtx = skim_folder + "AM\\SOV_skim.mtx"
    pm_sov_skim_mtx = skim_folder + "PM\\SOV_skim.mtx"
    am_transit_skim_mtx = skim_folder + "AM\\wat_for_all_tr_skim.mtx"
    pm_transit_skim_mtx = skim_folder + "PM\\wat_for_all_tr_skim.mtx"
    temp_sov_skim_mtx = out_folder + "temp_sov_skim.mtx"
    temp_transit_skim_mtx = out_folder + "temp_transit_skim.mtx"
    out_sov_skim_omx = out_folder + "sov_skim.omx"
    out_transit_skim_omx = out_folder + "transit_skim.omx"

    //find the MAPC TAZs
    lyrs = RunMacro("TCB Add DB Layers", taz_db)
    taz_lyr = lyrs[1]
    SetView(taz_lyr)
    n = SelectByQuery("mapcZ", "Several", "Select * where RPA = 'MAPC'",)

    sov_am_mtx = OpenMatrix(am_sov_skim_mtx,)
    sov_pm_mtx = OpenMatrix(pm_sov_skim_mtx,)
    transit_am_mtx = OpenMatrix(am_transit_skim_mtx,)
    transit_pm_mtx = OpenMatrix(pm_transit_skim_mtx,)

    //create indices on MAPC zones in each input matrix. Skip if indices already exist
    idx_arr = GetMatrixIndexNames(sov_am_mtx)
    ret = FindStrings(idx_arr[1], {{"=mapcZ"}},)
    if ret[1] = 0 then mapc_idx = CreateMatrixIndex("mapcZ", sov_am_mtx, "Both", taz_lyr+"|mapcZ", "ID", "ID",)

    idx_arr = GetMatrixIndexNames(sov_pm_mtx)
    ret = FindStrings(idx_arr[1], {{"=mapcZ"}},)
    if ret[1] = 0 then mapc_idx = CreateMatrixIndex("mapcZ", sov_pm_mtx, "Both", taz_lyr+"|mapcZ", "ID", "ID",)

    idx_arr = GetMatrixIndexNames(transit_am_mtx)
    ret = FindStrings(idx_arr[1], {{"=mapcZ"}},)
    if ret[1] = 0 then mapc_idx = CreateMatrixIndex("mapcZ", transit_am_mtx, "Both", taz_lyr+"|mapcZ", "ID", "ID",)

    idx_arr = GetMatrixIndexNames(transit_pm_mtx)
    ret = FindStrings(idx_arr[1], {{"=mapcZ"}},)
    if ret[1] = 0 then mapc_idx = CreateMatrixIndex("mapcZ", transit_pm_mtx, "Both", taz_lyr+"|mapcZ", "ID", "ID",)

    sov_am_mc = CreateMatrixCurrency(sov_am_mtx, "CongTime", "mapcZ", "mapcZ",)
    sov_pm_mc = CreateMatrixCurrency(sov_pm_mtx, "CongTime", "mapcZ", "mapcZ",)
    am_ivtt_mc = CreateMatrixCurrency(transit_am_mtx, "Total_IVTT", "mapcZ", "mapcZ",)
    am_ovtt_mc = CreateMatrixCurrency(transit_am_mtx, "Total_OVTT", "mapcZ", "mapcZ",)
    pm_ivtt_mc = CreateMatrixCurrency(transit_pm_mtx, "Total_IVTT", "mapcZ", "mapcZ",)
    pm_ovtt_mc = CreateMatrixCurrency(transit_pm_mtx, "Total_OVTT", "mapcZ", "mapcZ",)

    //Calculate average sov congested time by adding, cell by cell, the am and pm matrix currencies
    //and dividing the result by 2 (multiply by 0.5)
    mat = CombineMatrices(
        {sov_am_mc, sov_pm_mc}, 
        {{"File Name", temp_sov_skim_mtx},
        {"Label", "SOV_am_pm"},
        {"Operation", "Union"}}
    )

    //rename the cores in the new matrix
    cores = GetMatrixCoreNames(mat)
    cores[1] = "AM_CongTime"
    cores[2] = "PM_CongTime"
    SetMatrixCoreNames(mat, cores)

    //create the mapcZ index if it did not follow the source matrix currencies
    idx_arr = GetMatrixIndexNames(mat)
    ret = FindStrings(idx_arr[1], {{"mapcZ"}},)
    if ret[1] = 0 then mapc_idx = CreateMatrixIndex("mapcZ", mat, "Both", taz_lyr+"|mapcZ", "ID", "ID",)

    //add a new core to hold the composite skim and create matrix currencies for all cores
    AddMatrixCore(mat, "CongTime")
    sov_out_mc = CreateMatrixCurrency(mat, "CongTime", "mapcZ", "mapcZ",)
    
    Opts = Null
    Opts.Input.[Matrix Currency] = {temp_sov_skim_mtx, "CongTime", "mapcZ", "mapcZ"}
    Opts.Global.Method = 11 //formula
    Opts.Global.[Cell Range] = 2 // all cells
    Opts.Global.[Expression Text] = "([AM_CongTime] + [PM_CongTime]) / 2"
    Opts.Global.[Force Missing] = "No"
    ret = RunMacro("TCB Run Operation", "Fill Matrices", Opts, &list)

    //Copy the composite SOV skim matrix to an omx file
    //Note: CopyMatrix will copy all cores even though we specify just one
    sov_out_mat = CopyMatrix(sov_out_mc, 
        {{"File Name", out_sov_skim_omx},
        {"Label", "SOV"},
        {"File Based", "Yes"},
        {"OMX", "True"}
    })

    mapc_idx = Null
    sov_out_mc = Null 
    mat = Null 

    //Calculate average total transit travel time time by adding, cell by cell, the am and pm 
    //IVTT and OVTT matrix currencies
    //and dividing the result by 2 (multiply by 0.5)
    mat = CombineMatrices(
        {am_ivtt_mc, am_ovtt_mc, pm_ivtt_mc, pm_ovtt_mc}, 
        {{"File Name", temp_transit_skim_mtx},
        {"Label", "transit_am_pm"},
        {"Operation", "Union"}}
    )

    //rename the cores in the new matrix
    cores = GetMatrixCoreNames(mat)
    cores[1] = "AM_IVTT"
    cores[2] = "AM_OVTT"
    cores[3] = "PM_IVTT"
    cores[4] = "PM_OVTT"
    SetMatrixCoreNames(mat, cores)

    //create the mapcZ index if it did not follow the source matrix currencies
    idx_arr = GetMatrixIndexNames(mat)
    ret = FindStrings(idx_arr[1], {{"mapcZ"}},)
    if ret[1] = 0 then mapc_idx = CreateMatrixIndex("mapcZ", mat, "Both", taz_lyr+"|mapcZ", "ID", "ID",)

    //add a new core to hold the composite skim and create matrix currencies for all cores
    AddMatrixCore(mat, "TotalTime")
    transit_out_mc = CreateMatrixCurrency(mat, "TotalTime", "mapcZ", "mapcZ",)
    
    Opts = Null
    Opts.Input.[Matrix Currency] = {temp_transit_skim_mtx, "TotalTime", "mapcZ", "mapcZ"}
    Opts.Global.Method = 11 //formula
    Opts.Global.[Cell Range] = 2 // all cells
    Opts.Global.[Expression Text] = "([AM_IVTT] + [AM_OVTT] + [PM_IVTT] + [PM_OVTT]) / 2"
    Opts.Global.[Force Missing] = "No"
    ret = RunMacro("TCB Run Operation", "Fill Matrices", Opts, &list)

    //Copy the skim matrix to an omx file
    //Note: CopyMatrix will copy all cores even though we specify just one
    transit_out_mat = CopyMatrix(transit_out_mc, 
        {{"File Name", out_transit_skim_omx},
        {"Label", "SOV"},
        {"File Based", "Yes"},
        {"OMX", "True"}
    })

    mapc_idx = Null
    transit_out_mc = Null 
    mat = Null

    ret = RunMacro("G30 File Close All")
    DeleteFile(temp_sov_skim_mtx)
    DeleteFile(temp_transit_skim_mtx)
    
    ok = 1
    quit:
    return(ok)

endMacro