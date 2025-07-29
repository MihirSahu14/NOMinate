# Attempt to generate the character map again

# Create a new directed graph for Mane Pena's character map
G2 = nx.DiGraph()

# Define nodes
nodes = [
    "Mane Pena",
    "Feather",
    "Faith and Hope",
    "Mass Production",
    "Media Sensation",
    "Business",
    "Consumer Culture Exploitation",
    "Distorted Image"
]

# Define edges (connections)
edges = [
    ("Mane Pena", "Feather"),
    ("Feather", "Faith and Hope"),
    ("Feather", "Mass Production"),
    ("Feather", "Media Sensation"),
    ("Mass Production", "Consumer Culture Exploitation"),
    ("Mass Production", "Business"),
    ("Media Sensation", "Distorted Image"),
    ("Media Sensation", "Consumer Culture Exploitation"),
    ("Consumer Culture Exploitation", "Distorted Image"),
    ("Business", "Consumer Culture Exploitation")
]

# Add nodes and edges to the graph
G2.add_nodes_from(nodes)
G2.add_edges_from(edges)

# Draw the graph
plt.figure(figsize=(10, 7))
pos = nx.spring_layout(G2, seed=42)  # Positioning nodes
nx.draw(G2, pos, with_labels=True, node_color="lightblue", edge_color="black", node_size=3000, font_size=10, font_weight="bold")
plt.title("Mane Pena Character Map", fontsize=12)
plt.show()
