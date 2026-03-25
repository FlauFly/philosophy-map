import json
import pandas as pd

def fix_string(text):
    dummy = list(text)
    result = "".join(dummy[8:-1])
    return result

def extracting_graph(article):
    result_nodes = []
    result_connections = []

    # Dealing with first degree node (main article)

    first_element = df_nodes[df_nodes['id'] == article].to_dict(orient="records")[0]
    first_node = {"id": first_element['id'], "group": 1, "address": fix_string(first_element['address'])}
    result_nodes.append(first_node)

    # Dealing with second degree nodes (connected to main)

    sources_df = df_links[df_links["target"] == article]
    sources = sources_df["source"].values.tolist()
    
    targets_df = df_links[df_links["source"] == article]
    targets = targets_df["target"].values.tolist()

    second_group = list(set([*sources, *targets]))
    third_group = []

    for node in second_group:
        second_element_zero = df_nodes[df_nodes['id'] == node].to_dict(orient="records") 
        second_element = second_element_zero[0]
        second_node = {"id": second_element['id'], "group": 2, "address": fix_string(second_element['address'])}
        if second_node not in result_nodes:
            result_nodes.append(second_node)

    # Dealing with third degree nodes

    for node in second_group:
        sources_df = df_links[df_links["target"] == node]
        sources = sources_df["source"].values.tolist()

        targets_df = df_links[df_links["source"] == node]
        targets = targets_df["target"].values.tolist()

        for nodeDegree2 in list(set([*sources, *targets])):
            if (nodeDegree2 != article and nodeDegree2 not in second_group):
                third_group.append(nodeDegree2)
                third_element = df_nodes[df_nodes['id'] == nodeDegree2].to_dict(orient="records")[0]
                third_node = {"id": third_element['id'], "group": 3, "address": fix_string(third_element['address'])}
                if third_node not in result_nodes:
                    result_nodes.append(third_node)

    # Connections between main article (group 1) and group 2

    connections = df_links[(df_links["target"] == article) | (df_links["source"] == article)].to_dict(orient="records")
    for connection in connections:
        result_connections.append(connection)

    # Connections between group 2 and other group 2 elements or group 3 with exlusion of main article
    for node in second_group:
        connections = df_links[(df_links["target"] == node) | (df_links["source"] == node)].to_dict(orient="records")
        for connection in connections:
            if connection not in result_connections:
                result_connections.append(connection)

    # Connections between elements of group 3

    for node in third_group:
        target_connections = df_links[df_links["source"] == node]
        targets = target_connections["target"].values
        for target in targets:
            if target in third_group:
                connection = {'source': node, 'target': target}
                if connection not in result_connections:
                    result_connections.append(connection)

        source_connections = df_links[df_links["target"] == node]
        sources = target_connections["source"].values
        for source in sources:
            if source in third_group:
                connection = {'source': source, 'target': node}
                if connection not in result_connections:
                    result_connections.append(connection)

    data = {"nodes": result_nodes, "links": result_connections}

    # Exporting data to json file
    print("Starting export of " + article)
    final_adress = fix_string(df_nodes[df_nodes['id'] == article]['address'].values[0])
    json_str = json.dumps(data, indent=2)
    with open(f'datasets/{final_adress}.json', "w") as f:
        f.write(json_str)

    print("Done!")

with open('data.json', 'r') as file:
    data = json.load(file)

nodes = data["nodes"]
links = data["links"]

df_nodes = pd.DataFrame.from_dict(nodes)
df_links = pd.DataFrame.from_dict(links)

# articles = df_nodes['id'].to_list()

# for article in articles: 
# extracting_graph(article)

article = "Plato"

print(extracting_graph(article))
