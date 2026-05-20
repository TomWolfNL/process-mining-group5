import pm4py
import pandas as pd

def xes_to_csv():
    domesticDeclarations = pm4py.read_xes("Datasets/domesticDeclarations.xes")
    internationalDeclarations = pm4py.read_xes("Datasets/internationalDeclarations.xes")
    permitLog = pm4py.read_xes("Datasets/permitLog.xes")
    prepaidTravelCost = pm4py.read_xes("Datasets/prepaidTravelCost.xes")
    requestForPayment = pm4py.read_xes("Datasets/requestForPayment.xes")

    df_domesticDeclarations = pm4py.convert_to_dataframe(domesticDeclarations)
    df_internationalDeclarations = pm4py.convert_to_dataframe(internationalDeclarations)
    df_permitLog = pm4py.convert_to_dataframe(permitLog)
    df_prepaidTravelCost = pm4py.convert_to_dataframe(prepaidTravelCost)
    df_requestForPayment = pm4py.convert_to_dataframe(requestForPayment)

    df_domesticDeclarations.to_csv("Output/domesticDeclarations.csv", index=False)
    df_internationalDeclarations.to_csv("Output/internationalDeclarations.csv", index=False)
    df_permitLog.to_csv("Output/permitLog.csv", index=False)
    df_prepaidTravelCost.to_csv("Output/prepaidTravelCost.csv", index=False)
    df_requestForPayment.to_csv("Output/requestForPayment.csv", index=False)

def combine_Output():
    df_domesticDeclarations = pd.read_csv("Output/domesticDeclarations.csv")
    df_internationalDeclarations = pd.read_csv("Output/internationalDeclarations.csv")
    df_permitLog = pd.read_csv("Output/permitLog.csv")
    df_prepaidTravelCost = pd.read_csv("Output/prepaidTravelCost.csv")
    df_requestForPayment = pd.read_csv("Output/requestForPayment.csv")

    df_declarations = pd.concat(
        [df_domesticDeclarations, df_internationalDeclarations],
        ignore_index=True,
    )

    merged = (
        df_permitLog
        .merge(
            df_prepaidTravelCost,
            on="id",
            how="outer",
        )
        .merge(
            df_declarations,
            on="id",
            how="outer",
        )
        .merge(
            df_requestForPayment,
            left_on="case:Rfp_id",
            right_on="case:Rfp_id",
            how="outer",
            suffixes=("", "_rfp")
        )
    )

    merged.to_csv("Output/Combined.csv", index=False)

    merged["time:timestamp"] = pd.to_datetime(
        merged["time:timestamp"],
        errors="coerce",
        utc=True
    )

    merged = merged.dropna(subset=["time:timestamp"])
    
    event_log = pm4py.convert_to_event_log(merged)

    pm4py.write_xes(
        event_log,
        "Output/Combined.xes"
    )

def concat_Output():
    df_domesticDeclarations = pd.read_csv("Output/domesticDeclarations.csv")
    df_internationalDeclarations = pd.read_csv("Output/internationalDeclarations.csv")
    df_permitLog = pd.read_csv("Output/permitLog.csv")
    df_prepaidTravelCost = pd.read_csv("Output/prepaidTravelCost.csv")
    df_requestForPayment = pd.read_csv("Output/requestForPayment.csv")

    concat = pd.concat(
        [df_domesticDeclarations, df_internationalDeclarations, df_permitLog, df_prepaidTravelCost, df_requestForPayment],
        ignore_index=True,
    )

    concat.to_csv("Output/Concat.csv", index=False)

    concat["time:timestamp"] = pd.to_datetime(
        concat["time:timestamp"],
        errors="coerce",
        utc=True
    )

    concat = concat.dropna(subset=["time:timestamp"])
    
    event_log = pm4py.convert_to_event_log(concat)

    pm4py.write_xes(
        event_log,
        "Output/Concat.xes"
    )

combine_Output()