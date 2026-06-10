import pm4py
import pandas as pd
from pathlib import Path

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

    Path("output").mkdir(exist_ok=True)

    df_domesticDeclarations.to_csv("Output/domesticDeclarations.csv", index=False)
    df_internationalDeclarations.to_csv("Output/internationalDeclarations.csv", index=False)
    df_permitLog.to_csv("Output/permitLog.csv", index=False)
    df_prepaidTravelCost.to_csv("Output/prepaidTravelCost.csv", index=False)
    df_requestForPayment.to_csv("Output/requestForPayment.csv", index=False)

def combine_csv():
    df_domesticDeclarations = pd.read_csv("Output/domesticDeclarations.csv")
    df_internationalDeclarations = pd.read_csv("Output/internationalDeclarations.csv")
    df_permitLog = pd.read_csv("Output/permitLog.csv")
    df_prepaidTravelCost = pd.read_csv("Output/prepaidTravelCost.csv")
    df_requestForPayment = pd.read_csv("Output/requestForPayment.csv")
    
    rfp_matched = df_requestForPayment.merge(
        df_prepaidTravelCost[["case:Rfp_id", "id"]],
        on="case:Rfp_id",
        how="inner",
        suffixes=("_rfp", "_ptc")
    )
    rfp_matched["id"] = rfp_matched["id_ptc"]
    rfp_matched = rfp_matched.drop(columns=["id_rfp", "id_ptc"])

    concat = pd.concat(
        [
            df_domesticDeclarations,
            df_internationalDeclarations,
            df_permitLog,
            df_prepaidTravelCost,
            rfp_matched
        ],
        ignore_index=True
    )

    concat.to_csv("Output/Concat.csv", index=False)

    concat["time:timestamp"] = pd.to_datetime(
        concat["time:timestamp"],
        errors="coerce",
        utc=True
    )

    concat = concat[
        (concat["time:timestamp"].dt.year >= 2017) &
        (concat["time:timestamp"].dt.year <= 2019)
    ]

    concat = concat.drop_duplicates(
        subset=["id", "concept:name", "time:timestamp"]
    )

    concat = concat.sort_values(["id", "time:timestamp"])
    
    event_log = pm4py.convert_to_event_log(concat)

    pm4py.write_xes(
        event_log,
        "Output/Concat.xes"
    )

def create_petri_net():
    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(pm4py.read_xes("Output\Concat.xes"))

    pm4py.save_vis_petri_net(
        net,
        initial_marking,
        final_marking,
        "petri_net.png"
    )

if __name__ == "__main__":
    xes_to_csv()
    combine_csv()
    create_petri_net()