#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import argparse
import math
import osrm
import os.path
import re
import numpy as np
from shutil import copyfile
from tqdm import tqdm
import matplotlib.pyplot as plt

# ***********************************************************************************
# 	SCRIPT evaluate_fastest_paths [python 3]
#
# 	@brief Evaluate the fastest path between each point in an instance file, generating the distances and duration matrices
#
# 	@author Dario Vezzali
# 	@version 1.0.1
# 	@date May 23, 2019
# ***********************************************************************************

# -------------------------------------
# Deal with command line arguments
parser = argparse.ArgumentParser()

parser.add_argument('-i', '--instance',
                    action = "store",
                    dest = "instance_file",
                    help = "The path to the instance file",
                    required = True)
parser.add_argument('-o', '--output-folder',
                    action = "store",
                    dest = "output_folder",
                    help = "The output folder",
                    required = False)
parser.add_argument('-m', '--max-points-query',
                    action = "store",
                    dest = "max_points_per_query",
                    help = "The maximum number of points per query",
                    required = False)

# --------------------------------------------------------------------
# CLASS Point
# --------------------------------------------------------------------
class Point:
    def __init__(self, id, lat, lng, is_depot):
        self.id = id
        self.lat = float(lat)
        self.lng = float(lng)
        self.is_depot = is_depot
    
    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
        return ', '.join(sb)
     
    def __repr__(self):
        return self.__str__() 

# --------------------------------------------------------------------
# CLASS Arc
# --------------------------------------------------------------------
class Arc:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return '(' + str(self.x.id) + ', ' + str(self.y.id) + ')'
     
    def __repr__(self):
        return '(' + str(self.x.id) + ', ' + str(self.y.id) + ')'

# --------------------------------------------------------------------
# CLASS Colors
# --------------------------------------------------------------------
class Colors:
    green = "\033[32m"
    blue = "\033[34m"
    yellow = "\033[33m"
    red = "\033[31m"  
    black = "\033[30m"
    white = "\033[37m"
    cyan = "\033[36m"
    magenta = "\033[35m"
    none = "\033[0m"
    bold = "\033[;1m"
    underline = "\033[4m"
    reverse = "\033[;7m"

# --------------------------------------------------------------------
# FUNCTION processTour
# --------------------------------------------------------------------
def processTour(tour, osrm_client, distances, durations):
    list_coords = []
    for i in range(0, tour.size):
        list_coords.append([tour[i].lng, tour[i].lat])
    
    # Get the fastest route between the points in the tour
    result = osrm_client.route(coordinates=list_coords, continue_straight=False)

    # Get the distances from the result
    for k in range(0, len(result['routes'][0]['legs'])):
        distances[tour[k].id][tour[k+1].id] = result['routes'][0]['legs'][k]['distance']
        durations[tour[k].id][tour[k+1].id] = result['routes'][0]['legs'][k]['duration']

# --------------------------------------------------------------------
# Setup and declaration of main variables
# --------------------------------------------------------------------

# Parse arguments
args = parser.parse_args()

# Get the output folder
output_folder = "output"
if args.output_folder is not None:
    output_folder = args.output_folder

# Get the maximum number of points per query
max_points_per_query = 200 # Default value
if args.max_points_per_query is not None:
    max_points_per_query = int(args.max_points_per_query)

# Get the instance name
head, tail = os.path.split(args.instance_file)
instance_name = tail

points = [] # Initialize the list of points
#num_depots = 0
#num_services = 0
num_municipalities = 0

# --------------------------------------------------------------------
# Read the instance file
# --------------------------------------------------------------------
print(Colors.cyan, '>> Opening instance file...', Colors.none, sep='')
instance_file = tuple(open(args.instance_file, 'r'))
num_lines = len(instance_file)
index_line = 0

# --------------------------------------------------------------------
# Get the number of depots and services
# --------------------------------------------------------------------
print(Colors.cyan, '>> Getting the number of depots...', Colors.none, sep='')
while(index_line < num_lines):
    if instance_file[index_line].find("#numDepots") != -1:
        num_depots = int(instance_file[index_line + 1])
        index_line += 2
        break
    index_line += 1

print(Colors.cyan, '>> Getting the number of lockers...', Colors.none, sep='')
while(index_line < num_lines):
    if instance_file[index_line].find("#numLockers") != -1:
        num_municipalities = int(instance_file[index_line + 1])
        index_line += 2
        break
    index_line += 1

print(Colors.cyan, '>> Getting the number of municipalities...', Colors.none, sep='')
while(index_line < num_lines):
    if instance_file[index_line].find("#numMunicipalities") != -1:
        num_municipalities += int(instance_file[index_line + 1])
        index_line += 2
        break
    index_line += 1


# --------------------------------------------------------------------
# Get the points associated with the depots
# --------------------------------------------------------------------
print(Colors.cyan, '>> Getting depots coordinates...', Colors.none, sep='')
while(index_line < num_lines):
    if instance_file[index_line].find("#depots") != -1:
        index_line += 4 # Skip the header
        break
    index_line += 1

for i in range(0, num_depots):
    current_line = (" ".join(instance_file[index_line].split())).split(' ')
    print(current_line[0], current_line[1])
    points.append(Point(len(points), current_line[3], current_line[4], True))
    index_line += 1

# --------------------------------------------------------------------
# Get the points associated with the municipalities
# --------------------------------------------------------------------
print(Colors.cyan, '>> Getting municipalities coordinates...', Colors.none, sep='')
while(index_line < num_lines):
    if instance_file[index_line].find("#municipalities") != -1:
        index_line += 4 # Skip the header
        break
    index_line += 1

current_cout = 1
while(index_line < num_lines):
    current_line = (" ".join(instance_file[index_line].split())).split(' ')
    print(current_line)

    # Check if it's a valid line
    if current_line[0].isdigit():
        points.append(Point(len(points), current_line[2], current_line[3], False))
        if int(current_line[0]) != current_cout:
            print(Colors.cyan, '>> Expected id ', current_cout, ' but found ', current_line[0], Colors.none, sep='')

        current_cout += 1

    index_line += 1

# Safety check: Verify if there are as many points as expected
print(Colors.cyan, '>> Found a total of ', len(points), ' points', Colors.none, sep='')
print(points)
if len(points) != num_municipalities + num_depots:
    print(Colors.yellow, "## Warning: A total of ", num_municipalities + num_depots, " were expected, but ", len(points), " were parsed!", Colors.none, sep="")

# --------------------------------------------------------------------
# Evaluate the fastest paths
# --------------------------------------------------------------------
osrm_client = osrm.Client(host='http://localhost:5000')
num_points = len(points)
distances = np.full((num_points, num_points), -1, dtype=float)
durations = np.full((num_points, num_points), -1, dtype=float)
degree = np.full(shape=(num_points), fill_value=num_points-1, dtype=float)
current_arc = Arc(points[0], points[1])
current_tour = np.empty((0), dtype=Point) # Create an array with 'num_points' -1 values
num_arcs = num_points * num_points # The total number of arcs
num_covered_arcs = num_points # The number of arcs already covered. Initialized with num_points to account for the diagonal

print(Colors.cyan, '>> Using OSRM to evaluate the shortest paths...', Colors.none, sep='')
with tqdm(total = math.ceil((num_arcs - num_points) / max_points_per_query)) as progress_bar:
    while True:
        # Safety check: verify if we are not including an arc that was already considered in another tour
        if distances[current_arc.x.id][current_arc.y.id] != -1:
            print(Colors.yellow, '## Warning: Arc [', current_arc.x.id, ', ', current_arc.y.id, '] was already evaluated! Overwriting...', Colors.none, sep='')
        
        # Set the distance of the current arc to zero to indicate that the arc has been already used. This is not strictly necessary
        # but can help spot possible bugs
        distances[current_arc.x.id][current_arc.y.id] = -20

        current_tour = np.append(current_tour, current_arc.x) # Add the source point to the tour
        degree[current_arc.x.id] -= 1 # Decrease the degree of the source point
        num_covered_arcs += 1 # Increase the number of arcs covered

        # Check if a tour is complete
        if current_tour.size == max_points_per_query or num_covered_arcs == num_arcs:
            current_tour = np.append(current_tour, current_arc.y) # Add the last destination to the tour
            processTour(current_tour, osrm_client, distances, durations) # Get the fastest route connecting the points in the tour
            current_tour = np.empty((0), dtype=Point) # Reset the current tour
            progress_bar.update(1) # Update the progress bar

        # Exit flag
        if num_covered_arcs == num_arcs:
            break

        # Get the next arc
        found = False
        for i in range(0, num_points):
            if i != current_arc.y.id and distances[current_arc.y.id][i] == -1 and degree[i] > 0:
                current_arc = Arc(current_arc.y, points[i])
                found = True
                break

        # Deal with the next arc, which should return to the initial point
        if not found and num_covered_arcs == num_arcs - 1:
            current_arc = Arc(current_arc.y, points[0])

# --------------------------------------------------------------------
# Write the distance and duration matrices into the file
# --------------------------------------------------------------------
print(Colors.cyan, '>> Creating new instance file at "', output_folder, '/', instance_name, '"...', Colors.none, sep='')
copyfile(args.instance_file, output_folder + '/' + instance_name) # First copy the instance file

with open(output_folder + '/' + instance_name, "a") as new_instance:
    print(Colors.cyan, '>> Appending distance matrix...', Colors.none, sep='')
    new_instance.write('\n')
    new_instance.write('#distances\n')
    new_instance.write('{:>8} '.format(''))
    for i in range(0, num_points):
        new_instance.write('{:>8} '.format(i))
    new_instance.write('\n')

    for i in range(0, num_points):
        new_instance.write('{:>8} '.format(i))
        for j in range(0, num_points):
            if i == j:
                new_instance.write('{:>8} '.format(0.0))
            else:
                new_instance.write('{:>8} '.format(math.ceil(distances[i][j] / 10) / 100))
        new_instance.write('\n')

    print(Colors.cyan, '>> Appending duration matrix...', Colors.none, sep='')
    new_instance.write('\n')
    new_instance.write('#durations\n')
    new_instance.write('{:>8} '.format(''))
    for i in range(0, num_points):
        new_instance.write('{:>8} '.format(i))
    new_instance.write('\n')

    for i in range(0, num_points):
        new_instance.write('{:>8} '.format(i))
        for j in range(0, num_points):
            if i == j:
                new_instance.write('{:>8} '.format(0.0))
            else:
                new_instance.write('{:>8} '.format(math.ceil((durations[i][j] / 60) * 100) / 100))
        new_instance.write('\n')
            
# Plot the graph
# plt.imshow(distances, aspect="auto")
# plt.colorbar()
# plt.show()
