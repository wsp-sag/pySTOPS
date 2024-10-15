# %%
import os
import pandas as pd

output_dir = r"C:\Users\USLP095001\code\pytstops\pySTOPS\r_scripts\output_2"


Year = ["CUR/", "FUT/"]
Scenario = [
    "HBW",
    "All Other Purposes",
    "Special Market 1",
    "Special Market 1",
    "Special Market 1",
    "Special Market 1",
    "New Transit Trips",
    "Linked Transit TOP",
    " ",
    "PMT Difference",
    "VMT Difference",
]
# %%
rep = (len(Scenario) - 5) // 2
Transit_Type = ["Non-Transit Dependents", "Transit Dependents"] * rep + ["-"] * 5

Summary_Table = pd.DataFrame({"Scenario": Scenario, "Transit Type": Transit_Type})
# %%
for s in Year:
    mainDir = os.path.join(output_dir, s)
    print(mainDir)
    os.chdir(mainDir)

    table_nos = [
        "10.03",
        "10.04",
        "1021.03",
        "4.02",
        "4.03",
        "706.03",
        "769.03",
        "8.01",
        "958.03",
    ]
    table = []
    rows = []
    cols = []
    last_value = {}

    for table_no in table_nos:
        print(table_no)
        name = f"Table {table_no}.csv"
        t = pd.read_csv(name)
        r, c = t.shape

        last_row = t[t.iloc[:, 0] == "Total"].index[0]
        m = int(t.iloc[last_row, -1])

        table.append(t)
        rows.append(r)
        cols.append(c)
        last_value[table_no] = m

    HBW_NTD = last_value["769.03"] - last_value["706.03"]
    HBW_TD = last_value["706.03"]
    AOP_TD = last_value["958.03"] - HBW_TD
    AOP_NTD = last_value["1021.03"] - HBW_TD - HBW_NTD - AOP_TD
    SM1_NTD = 0
    SM1_TD = 0
    SM2_NTD = 0
    SM2_TD = 0
    SM3_NTD = 0
    SM3_TD = 0
    SM4_NTD = 0
    SM4_TD = 0
    NTT = last_value["4.02"]
    LTTOP = last_value["4.03"]
    PMT_Diff = last_value["8.01"]
    VMT_Diff = last_value["8.01"] / 1.1
    values = [
        HBW_NTD,
        HBW_TD,
        AOP_NTD,
        AOP_TD,
        SM1_NTD,
        SM1_TD,
        SM2_NTD,
        SM2_TD,
        SM3_NTD,
        SM3_TD,
        SM4_NTD,
        SM4_TD,
        NTT,
        LTTOP,
        0,
        PMT_Diff,
        VMT_Diff,
    ]

    Peak = pd.read_csv("Table 10.03.csv")
    Off_Peak = pd.read_csv("Table 10.04.csv")
    start_line = Peak[Peak.iloc[:, 0] == "Route_ID"].index[0] + 1
    end_line = Peak[Peak.iloc[:, 0] == "Total"].index[0]

    VehAsg = pd.DataFrame(
        {
            "Route_ID": Peak.iloc[start_line:end_line, 0],
            "Route Name": Peak.iloc[start_line:end_line, 1],
            "No_Build_PEAK": Peak.iloc[start_line:end_line, 6],
            "No_Build_OFF PEAK": Off_Peak.iloc[start_line:end_line, 6],
            "Build_PEAK": Peak.iloc[start_line:end_line, 9],
            "Build_OFF PEAK": Off_Peak.iloc[start_line:end_line, 9],
        }
    )

    if s == "CUR/":
        Summary_Table["Current"] = values
        os.chdir(output_dir)
        VehAsg.to_csv("Vehicle Assignment (CUR).csv", index=False, header=False)
    elif s == "FUT/":
        Summary_Table["Future"] = values
        os.chdir(output_dir)
        VehAsg.to_csv("Vehicle Assignment (FUT).csv", index=False, header=False)

print(Summary_Table)

os.chdir(output_dir)
Summary_Table.to_csv("Calculations.csv", index=False, header=False)

# %%
