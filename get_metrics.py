import pandas as pd
import wandb
import os

api = wandb.Api()
entity, project = "etastepe", "ml_monitoring"
runs = api.runs(entity + "/" + project)

summary_list, config_list, name_list = [], [], []
for run in runs:
    # .summary contains output keys/values for
    # metrics such as accuracy.
    #  We call ._json_dict to omit large files
    summary_list.append(run.summary._json_dict)

    # .config contains the hyperparameters.
    #  We remove special values that start with _.
    config_list.append({k: v for k, v in run.config.items() if not k.startswith("_")})

    # .name is the human-readable name of the run.
    name_list.append(run.name)

runs_df = pd.DataFrame(
    {"summary": summary_list, "config": config_list, "name": name_list}
)

df = pd.DataFrame.from_records(runs_df.summary)
df = df.drop(columns=["_wandb"])

path = "./data"
os.mkdir(path)
df.to_csv(f"{path}/data.csv", index=False)
