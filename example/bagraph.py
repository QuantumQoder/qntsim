import matplotlib.pyplot as plt
import networkx as nx

n=int(input())
G=nx.barabasi_albert_graph(n,2)
nx.draw(G, with_labels=True)
#plt.show()

# print((G.nodes))
# print((G.edges))

