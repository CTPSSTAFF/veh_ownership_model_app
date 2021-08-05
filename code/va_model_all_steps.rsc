Macro "Run_VA_Model" (Args)

    //These arguments are already specified in the massdot.model file for TC8 / TC9
    Args.InputFolder            = "D:\\Projects\\Exploratory_Modelling\\Inputs\\"
    Args.ScenarioFolder         = "D:\\Projects\\Exploratory_Modelling\\Scenarios\\Scen_00\\"
    Args.OutputFolder           = Args.ScenarioFolder + "Out\\"
    Args.Zone_DB                = "Statewide_TAZs_2017.dbd"
    Args.[AM SOV Skim Matrix]   = Args.OutputFolder + "AM\\SOV_skim.mtx"
    Args.[PM SOV Skim Matrix]   = Args.OutputFolder + "PM\\SOV_skim.mtx"

    //These arguments will need to be added to massdot.model or massdot.scenarios
    Args.[AM Transit Skim Matrix]   = Args.OutputFolder + "AM\\wat_for_all_tr_skim.mtx"
    Args.[PM Transit Skim Matrix]   = Args.OutputFolder + "PM\\wat_for_all_tr_skim.mtx"
    Args.VA_CodeFolder              = "D:\\Projects\\veh_ownership_model_app\\code\\"
    Args.VA_PreprocessScript        = "test_preprocess_trnscd06.bat"
    Args.VA_ApplyScript             = "test_run_trnscd06.bat"
    Args.VA_DataFolder              = "D:\\Projects\\veh_ownership_model_app\\test_data\\"

    //export highway and transit skims to OpenMatrix files
    //if something goes wrong, exit the macro
    result = RunMacro("export_skims", Args)
    if result=0 then goto quit

    //run the Python VA preprocessor scripts
    result = RunMacro("Generate_Inputs", Args)
    if result=0 then goto quit

    //run the Python VA model application scripts
    result = RunMacro("Apply_Model", Args)
    if result=0 then goto quit

    //for future development: a macro that assembles a land use table for trip generation
    //from va model output and other files

    quit:
endMacro

Macro "export_skims" (Args)

    on error do
        err_msg = GetLastError({"Reference Info": true})
        ShowMessage("Veh_Model_Test - Macro export_skims: " + err_msg)
        ok = 0
        goto quit
    end

    ret = RunMacro("TCB Init")

    //When VA model execution is incorporated within the flow chart model execution, 
    //these variables should be included in the model argmuments list
    input_folder = Args.InputFolder + "Databases\\"
    va_data_folder = Args.VA_DataFolder
    taz_db = input_folder + Args.Zone_DB
    am_sov_skim_mtx = Args.[AM SOV Skim Matrix]
    pm_sov_skim_mtx = Args.[PM SOV Skim Matrix]
    am_transit_skim_mtx = Args.[AM Transit Skim Matrix]
    pm_transit_skim_mtx = Args.[PM Transit Skim Matrix]
    temp_sov_skim_mtx = va_data_folder + "temp_sov_skim.mtx"
    temp_transit_skim_mtx = va_data_folder + "temp_transit_skim.mtx"
    out_sov_skim_omx = va_data_folder + "sov_skim.omx"
    out_transit_skim_omx = va_data_folder + "transit_skim.omx"

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
    ShowMessage("export_skims macro completed.")
    ok = 1
    quit:
    return(ok)

endMacro

Macro "Generate_Inputs" (Args)

    on error do
        err_msg = GetLastError({"Reference Info": true})
        ShowMessage("VA Model - Generate_Inputs: " + err_msg)
        ret = -1
        ok = 0
        goto quit
    end

    va_script = Args.VA_CodeFolder + Args.VA_PreprocessScript

    ret = RunProgram(va_script, {{"Maximize", "True"}})
    Pause(1000)
    ShowMessage("VA preprocessing completed with return code = " + i2s(ret) + ".")
    ok = 1
    quit:
    return(ok)
endMacro

Macro "Apply_Model" (Args)

    on error do
        err_msg = GetLastError({"Reference Info": true})
        ShowMessage("VA Model - Apply_Model: " + err_msg)
        ret = -1
        ok = 0
        goto quit
    end

    va_script = Args.VA_CodeFolder + Args.VA_ApplyScript

    ret = RunProgram(va_script, {{"Maximize", "True"}})
    Pause(1000)
    ShowMessage("VA model application completed with return code = " + i2s(ret) + ".")
    ok = 1
    quit:
    return(ok)
endMacro