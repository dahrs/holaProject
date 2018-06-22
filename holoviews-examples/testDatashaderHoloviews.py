#!/usr/bin/python
#-*- coding:utf-8 -*- 


#import datashader as ds
import pandas as pd
import numpy as np
import holoviews as hv
import networkx as nx
import datashader as ds
import matplotlib.pyplot as plt

from bokeh.io import show, output_file
from bokeh.plotting import figure, save
from bokeh.models.graphs import from_networkx

from holoviews.operation.datashader import datashade, shade, dynspread, rasterize, bundle_graph
from holoviews.operation import decimate

from datashader.utils import export_image
from datashader.bokeh_ext import InteractiveImage

#from IPython.display import display_html

#import datashader.transfer_functions as tf
	
def testDatashader():
	'''
	http://datashader.org/user_guide/1_Plotting_Pitfalls.html
	'''
	num = 10000
	np.random.seed(1)

	dists = {cat: pd.DataFrame.from_items([('x', np.random.normal(x,s,num)),
		('y', np.random.normal(y,s,num)),
		('val', val),
		('cat', cat)])
		for x, y, s, val, cat in 
		[(  2,  2, 0.03, 10, "d1"), 
		(  2, -2, 0.10, 20, "d2"), 
		( -2, -2, 0.50, 30, "d3"), 
		( -2,  2, 1.00, 40, "d4"), 
		(  0,  0, 3.00, 50, "d5")] 
		}

	df = pd.concat(dists, ignore_index=True)
	df["cat"] = df["cat"].astype("category")
	tf.shade(ds.Canvas().points(df, 'x', 'y'))
	return



def testHoloviews():
	''''''
	hv.extension('bokeh')
	hv.renderer('matplotlib')
	station_info = pd.read_csv('./assets/station_info.csv')
	#station_info.head()
	scatter = hv.Scatter(station_info, 'services', 'ridership')
	#htmlOutput
	#render(scatter, './output.html', {'html':htmlOutput})
	#BOKEH RENDERER	#http://holoviews.org/user_guide/Deploying_Bokeh_Apps.html
	hv.renderer('bokeh').save(scatter,'out')
	#IPYTHON RENDERER (works with dynamic maps by making a widget)   #http://holoviews.org/user_guide/Plots_and_Renderers.html
	#html = renderer.html(scatter)
	display_html(html, raw=True)
	return



def simpleHoloviewsGraph():
	hv.extension('bokeh') 
	#%opts Graph [width=400 height=400]
	N = 8
	node_indices = np.arange(N)
	#using index as indicator of the node number
	#source reveals the point of departure a1
	source = np.zeros(N) #every edge starts from node 0 - numpy array of zeros : [0. 0. 0. 0. 0. 0. 0. 0.]
	#target reveals the point of arrival a2
	target = node_indices #numpy array of range : [0 1 2 3 4 5 6 7]

	padding = dict(x=(-1.2, 1.2), y=(-1.2, 1.2)) #X and Y showed scale on the cartesian table 

	simple_graph = hv.Graph(((source, target),)).redim.range(**padding)
	hv.renderer('bokeh').save(simple_graph,'out')
	return


def explicitPathHoloviewsGraph():
	hv.extension('bokeh') 
	#%opts Graph [width=400 height=400]
	N = 8
	node_indices = np.arange(N)
	#using index as indicator of the node number
	#source reveals the point of departure a1
	source = np.zeros(N) #every edge starts from node 0 - numpy array of zeros : [0. 0. 0. 0. 0. 0. 0. 0.]
	#target reveals the point of arrival a2
	target = node_indices #numpy array of range : [0 1 2 3 4 5 6 7]

	padding = dict(x=(-1.2, 1.2), y=(-1.2, 1.2)) #X and Y showed scale on the cartesian table 

	simple_graph = hv.Graph(((source, target),)).redim.range(**padding)
	

	def bezier(start, end, control, steps=np.linspace(0, 1, 100)):
		return (1-steps)**2*start + 2*(1-steps)*steps*control+steps**2*end

	x, y = simple_graph.nodes.array([0, 1]).T

	paths = []
	for node_index in node_indices:
		ex, ey = x[node_index], y[node_index]
		paths.append(np.column_stack([bezier(x[0], ex, 0), bezier(y[0], ey, 0)]))
		
	bezier_graph = hv.Graph(((source, target), (x, y, node_indices), paths)).redim.range(**padding)
	hv.renderer('bokeh').save(bezier_graph,'out')


def myGraphTest():
	graphData = pd.read_csv('./myGraph.tsv', sep='\t')

	source = graphData['jobTitleNodeIndex'].values
	sourceLabels = graphData['jobTitleName'].values
	target = graphData['skillNodeIndex'].values
	targetLabels = graphData['skillName'].values

	padding = dict(x=(-1.2, 1.2), y=(-1.2, 1.2)) #X and Y showed scale on the cartesian table 

	myGraph = hv.Graph(((source, target),)).redim.range(**padding)
	hv.renderer('bokeh').save(myGraph,'out')


def myGraphTestBokehOnly():
	#path = "/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/edgeListNoWeight.tsv"
	path = "/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/holoviews-examples/myGraphEdgeList.tsv"

	g = nx.read_edgelist(path, delimiter='\t', nodetype=str, data=(('weight',float), ('color',str))) #the bigger the edgelist weight appears shorter 
	
	plot = figure(title="My graph", x_range=(-1.1,1.1), y_range=(-1.1,1.1))

	myGraph = from_networkx(g, nx.spring_layout, scale=2, center=(0,0), weight='weight') #the spring layout uses Fruchterman-Reingold force-directed algorithm to lay out the graph
	plot.renderers.append(myGraph)
	output_file('./out.html')	
	show(myGraph)


def myGraphTestSpringLayout():
	#EXAMPLE GRAPH EDGE LIST
	path = "/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/holoviews-examples/myGraphEdgeList.tsv"
	#100 000 PROFILES GRAPH EDGE LIST
	#path = "/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/edgeListNoWeight.tsv"
	
	g = nx.read_edgelist(path, delimiter='\t', nodetype=str, data=(('weight',float), ('color',str))) #the bigger the edgelist weight appears shorter 
	padding = dict(x=(-1.2, 1.2), y=(-1.2, 1.2)) #X and Y showed scale on the cartesian table 
	
	renderer = hv.renderer('bokeh')

	myGraph = hv.Graph.from_networkx(g, nx.spring_layout, nodes=None, weight='weight', iterations=100, scale=2, center=(0,0)) #the spring layout uses Fruchterman-Reingold force-directed algorithm to lay out the graph
	#myGraph.redim.range(**padding).opts(plot=dict(color_index='Type', edge_color_index='Weight'),
    #                                    style=dict(cmap=['blue', 'red']))
	myGraph = myGraph.redim.range(**padding).opts(plot=dict(height=800, width=1000, node_fill_color='color', edge_color_index='Weight'),
                                        style=dict(node_fill_color='red', cmap=['green', 'red']))
	renderer.save(myGraph,'out')


def myGraphTestFixedImage():
	#EXAMPLE GRAPH EDGE LIST
	#path = "/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/holoviews-examples/myGraphEdgeList.tsv"
	#100 000 PROFILES GRAPH EDGE LIST
	path = "/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/edgeListNoWeight.tsv"
	
	g = nx.read_edgelist(path, delimiter='\t', nodetype=str, data=(('weight',float), ('index',int))) #the bigger the edgelist weight appears shorter 

	#set colors for the nodes
	nodeColorsDict = getNodeColors(path)
	nx.set_node_attributes(g, name='color', values=nodeColorsDict)
	#position nodes using Fruchterman-Reingold force-directed algorithm 
	pos = nx.spring_layout(g, weight='weight', iterations=50, scale=2, center=(0,0))
	#draw nodes
	#nx.draw_networkx_nodes(g,pos)
	#draw edges
	#draw labels
	nx.draw(g, with_labels=True, node_size=25, node_color=list(nodeColorsDict.values()))
	#plot
	plt.axis('off')
	plt.savefig("grapheEchantillon.pdf")
	plt.show()


def getStartNodes(edgeListPath):
	'''
	gets the origin nodes names, aka, the nodes (vertex) from which the arc (edge) starts
	'''
	startNodesSet = set()
	with open(edgeListPath) as edgeListFile:
		line = edgeListFile.readline()
		while line:
			lineList = (line.replace('\n', '')).split('\t')
			startNodesSet.add(lineList[0])
			line = edgeListFile.readline()
	return startNodesSet


def getNodeColors(edgeListPath):
	'''
	asigns a color according to the start vertex (red) or end vertex (blue) of each arch
	'''
	nodeColorsDict = {}
	with open(edgeListPath) as edgeListFile:
		line = edgeListFile.readline()
		while line:
			lineList = (line.replace('\n', '')).split('\t')
			nodeColorsDict[lineList[0]] = nodeColorsDict.get(lineList[0], 'red')
			nodeColorsDict[lineList[1]] = nodeColorsDict.get(lineList[1], 'cyan')
			line = edgeListFile.readline()
	return nodeColorsDict


def myGraphTestSpringLayout2():
	hv.extension('bokeh')
	renderer = hv.renderer('bokeh')

	#EXAMPLE GRAPH EDGE LIST
	path = "/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/holoviews-examples/myGraphEdgeList.tsv"
	#100 000 PROFILES GRAPH EDGE LIST
	#path = "/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/edgeListNoWeight.tsv"
	
	g = nx.read_edgelist(path, delimiter='\t', nodetype=str, data=(('weight',float), ('index',int))) #the bigger the edgelist weight appears shorter 

	#set colors for the nodes
	nodeColorsDict = getNodeColors(path)
	nx.set_node_attributes(g, name='color', values=nodeColorsDict)
	#position nodes using Fruchterman-Reingold force-directed algorithm 
	#pos = nx.spring_layout(g, weight='weight', iterations=50, scale=2, center=(0,0))

	#nodes = hv.Nodes((x, y, node_indices, node_labels), vdims='Type')
	myGraph = hv.Graph.from_networkx(g, nx.spring_layout, nodes=None, weight='weight', iterations=50, scale=2, center=(0,0)) #the spring layout uses Fruchterman-Reingold force-directed algorithm to lay out the graph
	myGraph = hv.Graph(myGraph, label='Graphe echantillon (EDGES: 795046, VERTICES : JobTitles(3827) - Skills(7529)')
	#nodes = hv.Nodes((x, y, node_indices, node_labels), vdims='Type')
	#print(myGraph.nodes['index'])


	padding = dict(x=(-1.2, 1.2), y=(-1.2, 1.2)) #X and Y showed scale on the cartesian table 
	#myGraph = myGraph.redim.range(**padding).opts(plot=dict(height=800, width=1000, color_index='Type', edge_color_index='Weight'),
    #                                    style=dict(node_fill_color='red', cmap=['green', 'red']))
	myGraph = myGraph.redim.range(**padding).opts(plot=dict(height=800, width=1000, node_fill_color='color', edge_color_index='Weight'),
                                        style=dict(cmap=nodeColorsDict))

	interactImg = InteractiveImage(myGraph, create_image())

	#myGraph = rasterize(myGraph)
	renderer.save(interactImg,'out')



	


	

#THE EXPLANATION
#https://github.com/bokeh/datashader/issues/193

#TUTOS:
#http://holoviews.org/user_guide/Network_Graphs.html
#http://holoviews.org/reference/elements/bokeh/Graph.html
#http://holoviews.org/user_guide/Deploying_Bokeh_Apps.html



#####################################################
#COMMANDES
#####################################################

#testHoloviews()
#simpleHoloviewsGraph()
#explicitPathHoloviewsGraph()
#myGraphTest()
#myGraphTestBokehOnly()
#myGraphTestSpringLayout()
myGraphTestSpringLayout2()
#myGraphTestFixedImage()


#hv.help(hv.Graph)