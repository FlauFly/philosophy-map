import json
import pandas as pd

with open('data.json', 'r') as file:
    data = json.load(file)

nodes = data["nodes"]
links = data["links"]

article = 'Plato'

df_nodes = pd.DataFrame.from_dict(nodes)
df_links = pd.DataFrame.from_dict(links)

selected = df_links.loc[df_links['source'] == article]
print(selected["target"].values)

for target in selected['target'].values:
    print(target)