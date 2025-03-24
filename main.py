## Definir função que irá ler ficheiro .xml e gardar a informação em 
## dicionários para fácil utilização dos dados referentes à rede a
## examinar e estudar

import xml.etree.ElementTree as ET  # xml reader library
import networkx as nx
#....................Read from xml file to graph........................
def xml_read(filename):

	tree = ET.parse(filename) # parse the whole tree
	root = tree.getroot() # get the root node

	nodes = [] ## Dictionary list init
	for node in root.findall('.//{http://sndlib.zib.de/network}node'): ##  . - current node, // all sub elements
		node_data = { ## get the different "node" data for dictionary
			'id': node.attrib['id'],
			'x': float(node.find('{http://sndlib.zib.de/network}coordinates/{http://sndlib.zib.de/network}x').text),
			'y': float(node.find('{http://sndlib.zib.de/network}coordinates/{http://sndlib.zib.de/network}y').text)
		}
		nodes.append(node_data)

	links = []
	for link in root.findall('.//{http://sndlib.zib.de/network}link'):
		link_data = {
			'id': link.attrib['id'],
			'source': link.find('{http://sndlib.zib.de/network}source').text,
			'target': link.find('{http://sndlib.zib.de/network}target').text,
			'setupCost': float(link.find('{http://sndlib.zib.de/network}setupCost').text)
		}
		links.append(link_data)

	'''demands = [] 
	for demand in root.findall(".//{http://sndlib.zib.de/network}demand"):
		demand_data = {
			'id' : demand.attrib['id'],
			'source' : demand.find('{http://sndlib.zib.de/network}source').text,
			'target' : demand.find('{http://sndlib.zib.de/network}target').text,
			'demandValue' : float(demand.find('{http://sndlib.zib.de/network}demandValue').text)
		}
		demands.append(demand_data)'''
		# the networks from the lib come with demands, but in this program they're not used
	
	G = nx.Graph() # Create a graph
	
	for node in nodes: #Read nodes from dict
		G.add_node(node ['id'], x = node['x'], y = node['y'])
		
	for link in links:
		source = link['source']
		target = link['target']
		setup_cost = link['setupCost']
		G.add_edge(source, target, setup_cost=setup_cost)
		
	'''print ("\nNodes")
	for node in nodes: #for loop to print the list of dictionaries one by one
		print(node)
	print("\nLinks")
	for link in links:
		print(link)'''

	return G

def test_graph1():

	G = nx.Graph()
	
	nodes = [
		{'id': 'A'},
		{'id': 'B'},
		{'id': 'C'},
		{'id': 'D'},
		{'id': 'E'},
		{'id': 'F'},
		#{'id': 'X'},
		#{'id': 'Y'}
	]
	
	for node in nodes:
		G.add_node(node['id'])
	
	# Add edges with original setup costs
	edges = [
		{'id': 'link1','source': 'A', 'target': 'B', 'setup_cost': 1},
		{'id': 'link2','source': 'A', 'target': 'C', 'setup_cost': 2},
		{'id': 'link3','source': 'B', 'target': 'D', 'setup_cost': 1},
		#{'id': 'linknew1','source': 'X', 'target': 'Y', 'setup_cost': 1},
		#{'id': 'linknew2','source': 'Y', 'target': 'D', 'setup_cost': 1},
		{'id': 'link4','source': 'B', 'target': 'E', 'setup_cost': 2},#setup cost to 3 with linknew
		{'id': 'link5','source': 'C', 'target': 'D', 'setup_cost': 2},#setup cost to 3 with linknew
		{'id': 'link6','source': 'D', 'target': 'F', 'setup_cost': 1},
		{'id': 'link7','source': 'E', 'target': 'F', 'setup_cost': 2}
	]
	
	for edge in edges:
		source = edge['source']
		target = edge['target']
		setup_cost = edge['setup_cost']
		G.add_edge(source, target, setup_cost=setup_cost)
	
	'''print ("\nNodes")
	for node in nodes: #for loop to print the list of dictionaries one by one
		print(node)
	print("\nEdges")
	for edge in edges:
		print(edge)'''
	
	return G
	
	#..............Two step approach function...........................
def TSA(G, node1, node2):
	# Initialize distances to all nodes as infinity
	traversed_edges = set() #set for path links
	H  = G.copy()
	try:
		dijkstra_res = nx.dijkstra_path(G, node1, node2, weight = 'setup_cost') #from node1 from and node 2 to as exemple
		edges_cost1 = nx.dijkstra_path_length(G, node1, node2, weight = 'setup_cost')
	except nx.NodeNotFound:
		print("Starting node not found.\n")
		return 1
	except nx.NetworkXNoPath:
		print("No path1 found.\n")
		dijkstra_res = ()
		edges_cost1 = float('inf')
	for n_idx in range(len(dijkstra_res)-1): # For loop to eliminate 1st dijkstra path from graph links
		traversed_edges.add((dijkstra_res[n_idx], dijkstra_res[n_idx+1]))
		H.remove_edge(dijkstra_res[n_idx], dijkstra_res[n_idx+1])
	try:
		tsa_res = nx.dijkstra_path(H, node1, node2, weight = 'setup_cost')
		edges_cost2 = nx.dijkstra_path_length(H, node1, node2, weight = 'setup_cost')
	except nx.NetworkXNoPath:
		print("No path2 found.\n")
		tsa_res = ()
		edges_cost2 = float('inf')
	return(dijkstra_res, edges_cost1, tsa_res, edges_cost2)
	
	#..............Suurballe Algorithm..................................5
	
def suurballe(H, node1, node2):
	G = H.copy()
	#print("\nsuurballe:::::::::::::::::::::::::::.\n")
	"""Find two edge-disjoint paths from source to target using the Suurballe algorithm."""
	# Step 1: Compute shortest path and lengths from the source node
	path1 = nx.dijkstra_path(G, node1, node2, weight='setup_cost')
	#print("PATH1: ", path1)
	#print("\nPath1:", path1)
	lengths, paths = nx.single_source_dijkstra(G, node1, weight='setup_cost') ##shortest path tree
	#print(lengths)
	#print(paths)
	# Update costs:
	G_modified = G.copy()
	for u, v in G.edges:
		#print(u,v)
		original_cost = G[u][v]['setup_cost']
		#print("OG cost",original_cost)
		distance_from_source_v = lengths[v]
		#print("v",distance_from_source_v)
		distance_from_source_u = lengths[u]
		#print("u",distance_from_source_u)
		modified_cost = original_cost - distance_from_source_v + distance_from_source_u
		G_modified[u][v]['setup_cost'] = modified_cost
		#print(u,v)
		#print(G_modified[u][v]['setup_cost'])
		
	# Step 3: Create a residual graph formed from G by removing 
	#the edges of G on path1 that are directed into s and then reverse the direction of the zero length
	G_inter = G_modified.copy()
	i = 0
	while i < len(path1)-1:
		u = path1[i]
		v = path1[i+1]
			# Remove edge directed into the target node
		if G_inter.has_edge(u, v):
			G_inter.remove_edge(u, v)
		i+=1
	'''for u,v in G_inter.edges:	
		print(u,v)
		print(G_inter[u][v]['setup_cost'])
	'''	
	#print("::::::::::::::::::::::::::::")
			
	G_residual = G_inter.copy()
	for i in range(len(path1) - 1):
		u, v = path1[i], path1[i + 1]
			# Reverse the direction of zero-length edge
		if G_residual.has_edge(u, v) and G_residual[u][v]['setup_cost'] == 0:
			G_residual.remove_edge(u, v)
		G_residual.add_edge(v, u,setup_cost=0)
	'''for u,v in G_residual.edges:
			print(u,v)
			print(G_residual[u][v]['setup_cost'])
	'''		
	# Step 4: Find the shortest path2 in the residual graph by running Dijkstra's algorithm
	path2 = nx.dijkstra_path(G_residual, node1, node2, weight='setup_cost')
	#print("Path2: ", path2)
	
	# Step 5: Discard the reversed edges of P2 from both paths
	#print ("path1:", path1)
	#print ("path2:", path2)
	#print("-----------------")
	rev_path2 = path2[::-1] # reverse the 2nd path
	#print("Rev_Path2:", rev_path2)
	#print("\n\n")
	i = 1 #counters for path1 joint edge start
	j = 1 #counters for path2 joint edge start
	edge_len = 0 #joint edge length
	path1_dij = path1 
	path2_dij = path2
	
	if (len(path1)) <= 2 or len(rev_path2) <=2: #If there's only two nodes, no need to take edges
		path1_dij = path1						# it's aready disjointed
		path2_dij = path2
	else:
		while i < (len(path1) - 1):
			node1 = (path1[i]) #check from node 2 (list[1]) to last but one
			i+= 1
			#print("1:",node1)
			while j < (len(rev_path2) - 1):#chck path 2
				node2 = (rev_path2[j]) 
				#print("2:",node2)
				j+= 1
				if node1 == node2: #check if node from path1 = node from path2
					dij_flag = 0
					joint_count1 = i
					joint_count2 = j
					while node1 == node2:
						node1 = path1[joint_count1+1]
						node2 = rev_path2[joint_count2+1]
						#print ("inside:")
						edge_len+=1
						joint_count1+=1 # to count how many nodes are repeated on both paths
						joint_count2+=1 # same for 2nd path
					else:
						path11 = path1[:i] #Dividing by parts, here 1st part of 1st path
						#print("11:",path11)
						path12 = rev_path2[:j-1] # 2nd part of 1st path
						path12.reverse()
						#print("12:", path12)
						path21 = rev_path2[j+edge_len:] # 1st part of 2nd path
						path21.reverse()
						#print("21:", path21)
						path22 = path1[i+edge_len-1:] # 2nd part of 2nd path
						#print("22:", path22)
						path1 = path11+path12 # concatenate the two parts
						path2 = path21+path22 # same
						#print("new p1:",path1)
						#print("new p2:",path2)
						#print("i",i,"j",j,"len",edge_len)
					path1_dij = path1 # if there's no equal edges, then the paths are already disjoited
					path2_dij = path2
					

	path1_cost = 0
	for i in range(len(path1_dij)-1):
		u,v = path1_dij[i],path1_dij[i+1]
		path1_cost = path1_cost + H[u][v]['setup_cost']
	path2_cost = 0
	for i in range(len(path2_dij)-1):
		u,v = path2_dij[i],path2_dij[i+1]
		path2_cost = path2_cost + H[u][v]['setup_cost']
	return path1_dij, path1_cost, path2_dij, path2_cost
	
def res_rate (G):
	H = nx.DiGraph(G)
	tsa_paths_nr = 0 #number of paths calculated w/ TSA
	suu_paths_nr = 0 #number of paths calculated w/ Suurballe
	optimal_tsa = 0 #counter for how many optimal paths are calulated w/ TSA
	tsa_cost_mean = 0 # Cost of all paths using tsa
	suu_cost_mean = 0 # Cost of all paths using Suurballe
	#Resolution rate of TSA for finding a solution even if it's not the optimal one
	for node1 in G.nodes:
		for node2 in G.nodes:
			if node1 != node2:
				tsa1, tsa1_cost, tsa2, tsa2_cost = TSA (G,node1,node2)
				#print("TSA: ", node1, node2, ":: Cost 1: ",tsa1_cost,"; Cost 2: ", tsa2_cost)
				if tsa1 != () and tsa2 != (): ## If there's no second path, dont count it
					tsa_paths_nr = tsa_paths_nr + 1
					tsa_cost_mean = tsa_cost_mean + tsa1_cost + tsa2_cost
	print()
	for node1 in G.nodes:
		for node2 in G.nodes:
			if node1 != node2:
				disjoint1, dij1_cost, disjoint2, dij2_cost = suurballe(H, node1, node2)
				#print("Suurballe: ", node1, node2, ":: Cost 1: ",dij1_cost,"; Cost 2: ", dij2_cost)
				if disjoint1 != () and disjoint2 != ():
					suu_paths_nr = suu_paths_nr + 1 
					suu_cost_mean = suu_cost_mean + dij1_cost + dij2_cost
	print("\n:::::::::::::::::::::::::::::::::::::::::::::::\n")
	print("Nr of paths using TSA: ", tsa_paths_nr)
	print("Nr of paths using Suurballe: ", suu_paths_nr)
	print("TSA resolution rate: ", tsa_paths_nr/suu_paths_nr)
	print("\n")
	#calculate Optimal resolution rate for TSA
	for node1 in G.nodes:
		for node2 in G.nodes:
			if node1 != node2:
				tsa1, tsa1_cost, tsa2, tsa2_cost = TSA (G,node1,node2)
				disjoint1, dij1_cost, disjoint2, dij2_cost = suurballe(H, node1, node2)
				if tsa1 == disjoint1 and tsa2 == disjoint2 or tsa2 == disjoint1 and tsa1 == disjoint2:
					optimal_tsa = optimal_tsa + 1
				#else:
					#print ("tsa: ",tsa1,"tsa2: ", tsa2, "suurb1: ", disjoint1, "suurb2: ", disjoint2)
	print("\n:::::::::::::::::::::::::::::::::::::::::::::::\n")
	print("Optimal paths using TSA: ", optimal_tsa)
	print("Suurballe nr of Paths: ", suu_paths_nr)
	print("TSA optimal resolution rate: ", optimal_tsa/suu_paths_nr)
	#Calculate the error cost mean
	print("\n")
	print("Mean cost of TSA: ",tsa_cost_mean/tsa_paths_nr)
	print("Mean Cost of Suurballe: ",suu_cost_mean/suu_paths_nr)
	print("Mean cost error diference: ",(tsa_cost_mean/tsa_paths_nr)-(suu_cost_mean/suu_paths_nr)) ##!!! IF NEGATIVE, THERE'S PATHS THAT TSA CAN'T CALCULATE!!!
	
def node_checker(G,in_node): #when selecting node, check if indeed there's that node on the graph
	node_flag = 0
	for node in G.nodes:
		if in_node == node:
			node_flag = 1
	while(node_flag == 0):
		in_node = input("The node is non-existent, please check existence or spelling:\n")
		for node in G.nodes:
			if in_node == node:
				node_flag = 1
	return(in_node)

def main ():
	## if cases for user interface (work in progress) change i for different accesses
	print("Welcome to TSA & Suurballe algorithm graph analyzer\n")
	i = input("Please select which network to use \n1.Polska\n2.france\n3.atlanta\n4.newyork\n5.test_graph1\nq.exit\n")
	
	if (i == '1'):
		filename = (r"./polska.xml") #r for raw string to avoid missinterpretation of special char
		G = xml_read(filename)
		print ("\nNodes:\n")
		for node in G.nodes: #for loop to print the list of dictionaries one by one
			print(node)
		node1 = input("\nSelect 1st node;\n")
		node1 = node_checker(G,node1)
		
		node2 = input("\nSelect 2nd node;\n")
		node2 = node_checker(G,node2)

		H = nx.DiGraph(G)

	elif (i == '2'):
		filename = (r"./france.xml")
		G = xml_read(filename)
		
		print ("\nNodes:\n")
		for node in G.nodes: #for loop to print the list of dictionaries one by one
			print(node)
		node1 = input("\nSelect 1st node;\n")
		node1 = node_checker(G,node1)
		
		node2 = input("\nSelect 2nd node;\n")
		node2 = node_checker(G,node2)
		
		H = nx.DiGraph(G) 
		
	elif (i == '3'):
		filename = (r"./atlanta.xml")
		G = xml_read(filename)
		print ("\nNodes:\n")
		for node in G.nodes: #for loop to print the list of dictionaries one by one
			print(node)
		node1 = input("\nSelect 1st node;\n")
		node1 = node_checker(G,node1)
		
		node2 = input("\nSelect 2nd node;\n")
		node2 = node_checker(G,node2)
		
		H = nx.DiGraph(G) 
		
	elif (i == '4'):
		filename = (r"./newyork.xml")
		G = xml_read(filename)
		print ("\nNodes:\n")
		for node in G.nodes: #for loop to print the list of dictionaries one by one
			print(node)
		node1 = input("\nSelect 1st node;\n")
		node1 = node_checker(G,node1)
		
		node2 = input("\nSelect 2nd node;\n")
		node2 = node_checker(G,node2)
		
		H = nx.DiGraph(G) 
		
	elif (i == '5'):
		G = test_graph1()
		print ("\nNodes:\n")
		for node in G.nodes: #for loop to print the list of dictionaries one by one
			print(node)
		node1 = input("\nSelect 1st node;\n")
		node1 = node_checker(G,node1)
		
		node2 = input("\nSelect 2nd node;\n")
		node2 = node_checker(G,node2)
		
		H = nx.DiGraph(G)
	elif (i == 'q'):
		return 0
	else:
		print("Choose an option from the above.")
		
	#nx.draw(G, pos = (G.node['x'],G.node['y']))
	
	option = input("\n\nSelect functionality;\n1.TSA\n2.Suurballe's Algorithm\n3.Resolution Rates(full Network)\nq.Exit\n\n")
	
	if option == '1':
		dijkstra_res, dij_cost, tsa_res, tsa_cost = TSA(G, node1, node2)
		
		print("\n\n1st path TSA: \n",dijkstra_res)
		print("\nCost: \n", dij_cost)
		
		print("\n2nd path TSA: \n",tsa_res)
		print("\nCost: \n", tsa_cost)
		
	elif option == '2':
		
		disjoint1, dij1_cost, disjoint2, dij2_cost = suurballe(H, node1, node2)

		print ("\n:::::::::::::::::::::::::::::::::::::::::::::::::\n")
		print("\n Disjointed path 1:\n", disjoint1)
		print("\n Disjointed cost 1:\n", dij1_cost)
		print("\n Disjointed path 2:\n", disjoint2)
		print("\n Disjointed cost 2:\n", dij2_cost)
	
	elif option == '3':
		print ("\n:::::::::::::::::::::::::::::::::::::::::::::::::\n")
		res_rate(G)
		
	elif (i == 'q'):
		return 0
	
	else:
		print("Choose an option from the above.")

if __name__ == "__main__":
	main()
