import json
import pandas as pd

def fix_string(text):
    dummy = list(text)
    result = "".join(dummy[8:-1])
    return result

with open('data.json', 'r') as file:
    data = json.load(file)

nodes = data["nodes"]

df_nodes = pd.DataFrame.from_dict(nodes)

df_result = df_nodes.filter(['id', 'address'], axis=1)
df_result = df_result.rename(columns={"id": "title", "address": "id"})
df_result["id"] = df_result['id'].str[8:-1]

result = df_result.to_dict(orient="records")
print(result)

# Exporting data to json file
print("Starting export")
json_str = json.dumps(result, indent=2)
with open("articles.json", "w") as f:
    f.write(json_str)

print("Done!")