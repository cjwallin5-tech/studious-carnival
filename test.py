from app.graph.graph import DirectedGraph
from app.graph.algorithms import all_paths

graph = DirectedGraph()

graph.add_node("A")
graph.add_node("B")
graph.add_node("C")

graph.add_edge("A", "B")
graph.add_edge("B", "C")

paths = all_paths(graph, "A", "C")
print(paths)