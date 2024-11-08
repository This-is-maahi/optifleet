#OptiFleet: Real-Time Fleet Optimistaion using Kruskal's MST
#purpose: Optimise urban transportation routes in high-demand
#Author: Kothuru Sai Mahidar

import matplotlib.pyplot as plt
import networkx as nx
import time


class UnionFind:
    """
    Union-Find Data Structure for managing disjoint sets in Kruskal's MST algorithm.
    Keeps track of connected components to avoid cycles in graph.
    """
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, node):
        """
        Find the root representative of the node, applying path compression.
        :param node: The node to find the root for.
        """
        if self.parent[node] != node:
            self.parent[node] = self.find(self.parent[node])
        return self.parent[node]

    def union(self, node1, node2):
        #Union two subsets into a single set.
        root1 = self.find(node1)
        root2 = self.find(node2)

        if root1 != root2:
            if self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            elif self.rank[root1] < self.rank[root2]:
                self.parent[root1] = root2
            else:
                self.parent[root2] = root1
                self.rank[root1] += 1


class KruskalMST:
    """
    Implementing  Kruskal's(MST) algorithm for route optimization.
    Using edges with weights that represent passenger demand to create an efficient spanning tree.
    """
    def __init__(self, vertices):
        self.V = vertices  # Total number of vertices (locations)
        self.edges = []  # Store edges as (start, end, weight) tuples

    def add_edge(self, start, end, weight):
        """
        :param start: Starting vertex of the edge.
        :param end: Ending vertex of the edge.
        :param weight: Weight (demand) of the edge.
        """
        self.edges.append((weight, start, end))

    def find_mst(self):
        """
        Execute Kruskal's algorithm to find the MST based on current edges.
        :return: List of edges in the MST.
        """
        self.edges.sort()  # Sort edges by weight (ascending)
        union_find = UnionFind(self.V)
        mst = []
        plt.ion()  # Turn on interactive plotting
        
        # Step 1: Display initial graph with all edges
        self.visualize_initial_graph()

        for weight, start, end in self.edges:
            if union_find.find(start) != union_find.find(end):
                union_find.union(start, end)
                mst.append((start, end, weight))
                self.visualize_step(mst, start, end, weight)
                time.sleep(1)  # Pause to visualize step-by-step
         

        # Step 3: Display final MST structure
        self.visualize_final_mst(mst)
        plt.ioff()
        plt.show()

        return mst


    def visualize_initial_graph(self):
        """Displays the initial graph with all edges and weights."""
        plt.clf()
        G = nx.Graph()
        for weight, u, v in self.edges:
            G.add_edge(u, v, weight=weight)

        pos = nx.spring_layout(G, seed=42)
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10, edge_color='gray')
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
        plt.title("Initial Graph with All Routes and Demand Weights")
        plt.pause(2)

    def visualize_step(self, mst_edges, latest_start, latest_end, latest_weight):
        """Visualizes the MST after each edge addition with emphasis on the latest added edge."""
        plt.clf()
        G = nx.Graph()
        for weight, u, v in self.edges:
            G.add_edge(u, v, weight=weight)

        pos = nx.spring_layout(G, seed=42)
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10, edge_color='lightgray')
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

        # Highlight MST edges in blue and the latest edge in red
        mst_graph = nx.Graph()
        for u, v, weight in mst_edges:
            mst_graph.add_edge(u, v, weight=weight)
        nx.draw(mst_graph, pos, with_labels=True, node_color='lightblue', edge_color='blue', width=2, node_size=500)

        # Highlight the latest edge in red
        nx.draw_networkx_edges(G, pos, edgelist=[(latest_start, latest_end)], edge_color='red', width=2.5)
        
        plt.title(f"Building MST - Latest Edge ({latest_start}-{latest_end}) with Demand: {latest_weight}")
        plt.pause(1)

    def visualize_final_mst(self, mst_edges):
        """Displays the final MST graph structure."""
        plt.clf()
        G = nx.Graph()
        for weight, u, v in self.edges:
            G.add_edge(u, v, weight=weight)

        pos = nx.spring_layout(G, seed=42)
        
        # Draw all edges in light gray
        nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='lightgray', node_size=500, font_size=10)
        
        # Draw only MST edges in green
        mst_graph = nx.Graph()
        for u, v, weight in mst_edges:
            mst_graph.add_edge(u, v, weight=weight)
        
        nx.draw(mst_graph, pos, with_labels=True, node_color='lightblue', edge_color='green', width=2.5, node_size=500)
        labels = nx.get_edge_attributes(mst_graph, 'weight')
        nx.draw_networkx_edge_labels(mst_graph, pos, edge_labels=labels)

        plt.title("Final MST with Optimized Routes")
        plt.pause(2)


class OptiFleetData:
    """
    Data Manager for real-time passenger volumes, storing demand between locations.
    Adjusts weights of edges dynamically to reflect current demand.
    """
    def __init__(self):
        self.demand_data = {}

    def update_passenger_volume(self, start, end, volume):
        """
        Update or add passenger volume for a specific route.
        :param start: Starting location ID.
        :param end: Destination location ID.
        :param volume: Volume of passengers between the locations.
        """
        self.demand_data[(start, end)] = volume

    def get_edges_with_demand(self):
        """
        Convert demand data to edge format compatible with MST.
        :return: List of edges with updated demand weights.
        """
        return [(start, end, volume) for (start, end), volume in self.demand_data.items()]


class OptiFleet:
    #Core class for Optifleet intended to handle real-time data updates and route optimizations
    def __init__(self,vertices):
        self.vertices = vertices
        self.mst_solver = KruskalMST(vertices)
        self.data_manager = OptiFleetData()
    def update_passenger_data(self, start, end,volume):
        """
        update passenger volume between location and add as edge in MST
        :param start: Starting location ID
        :param end: Ending/Destinaion location ID
        :param volume: Passenger volume between start and end(weight for edges)
        """
        self.data_manager.update_passenger_volume(start, end, volume)
        self.mst_solver.add_edge(start, end, volume)

    def build_routes(self):
        """
        Build Optimal routes using MST based on current passenger_data
        :return: List of selected routes with demand between locations
        """
        edges = self.data_manager.get_edges_with_demand()
        for start, end, volume in edges:
            self.mst_solver.add_edge(start, end, volume)
        
        #find and return optimised routes
        mst_routes = self.mst_solver.find_mst()
        print("\nOptimal Routes (based on current demand):")
        for start, end, volume in mst_routes:
            print(f"Route from {start} to {end} with demand: {volume}")
        return mst_routes

# Main execution with user input
if __name__ == "__main__":
    print("Welcome to OptiFleet - Dynamic Fleet Optimization System\n")
     # Initialize the OptiFleet system for a network with 6 locations
    optifleet = OptiFleet(vertices=6)
    
    # Simulate updates to passenger demand between various locations
    optifleet.update_passenger_data(0, 1, 15)
    optifleet.update_passenger_data(0, 2, 10)
    optifleet.update_passenger_data(1, 3, 5)
    optifleet.update_passenger_data(1, 4, 20)
    optifleet.update_passenger_data(2, 3, 8)
    optifleet.update_passenger_data(3, 5, 12)

    # Generate the optimized routes based on real-time passenger data
    optifleet.build_routes()

    # #dynamic input
    # # Step 1: Define the number of locations with error handling
    # while True:
    #     try:
    #         vertices = int(input("Enter the number of locations (vertices): "))
    #         if vertices <= 0:
    #             raise ValueError("The number of locations must be a positive integer.")
    #         break
    #     except ValueError as e:
    #         print(f"Invalid input: {e}. Please try again.")

    # optifleet = OptiFleet(vertices=vertices)

    # # Step 2: Define the number of edges/routes with error handling
    # while True:
    #     try:
    #         num_edges = int(input("Enter the number of routes (edges) between locations: "))
    #         if num_edges <= 0:
    #             raise ValueError("The number of routes must be a positive integer.")
    #         break
    #     except ValueError as e:
    #         print(f"Invalid input: {e}. Please try again.")

    # # Step 3: Input passenger demand between locations for each route
    # print("\nEnter routes and their respective passenger volumes (demand):")
    # for i in range(num_edges):

        
    #     while True:
    #         try:
    #             start = int(input(f"\nRoute {i + 1} - Start Location (ID): "))
    #             end = int(input(f"Route {i + 1} - End Location (ID): "))
    #             volume = int(input(f"Route {i + 1} - Passenger Volume (demand): "))

    #             if start < 0 or end < 0:
    #                 raise ValueError("Location IDs must be non-negative integers.")
    #             if volume < 0:
    #                 raise ValueError("Passenger volume must be a non-negative integer.")

    #             optifleet.update_passenger_data(start, end, volume)
    #             break  # Exit the loop after successful input
    #         except ValueError as e:
    #             print(f"Invalid input: {e}. Please try again.")

    # Step 4: Build and display the optimized routes
   # optifleet.build_routes()
