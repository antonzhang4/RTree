import time
import os
def load_data_points(points_file):
    points = []
    with open(points_file, 'r') as dataset: #open the 150,000 data points dataset
        for data in dataset.readlines(): #Read each line of the dataset
            data = data.split() #split the data so that each line is stored as a list of points
            points.append({ #We can now store variables after the data is now separately into a list
                'id': int(data[0]),
                'x': int(data[1]),
                'y': int(data[2])
                })
    dataset.close()
    return points

#load_queries uses the same approach as load_data_points to store data about the coordinates and ids of data points and queries 
def load_queries(queries_file):
    queries = []
    with open(queries_file, 'r') as dataset: 
        for data in dataset.readlines():
            data = data.split() 
            queries.append({ 
                'id': int(data[0]),
                'x1': int(data[1]),
                'x2': int(data[2]),
                'y1': int(data[3]),
                'y2': int(data[4])
                })
    dataset.close()
    return queries

#Used to write the results of sequential and rtree search into an output text file
def save_results(results, output_file):
    with open(output_file, 'w') as dataset:
        for result in results: #for each line of the output text file, write the number of points within a query
            dataset.write(str(result) + '\n')
    dataset.close()

def sequential_scan(points, query):
    start = time.time() #Start recording the time for each query
    count = 0 #Count the number of points found inside the query
    #Store the details of each query in variables
    query_id = query['id'] 
    x1 = query['x1']
    x2 = query['x2']
    y1 = query['y1']
    y2 = query['y2']
    for point in points: #Loop through the points
        #Store the details of each point in variables
        point_id = point['id']
        x = point['x']
        y = point['y']
        #Make sure that the x and y coordinate of the data point is between the min and max x and y coordinates of the query rectangle
        if int(x) >= int(x1) and int(x) <= int(x2) and int(y) >= int(y1) and int(y) <= int(y2): 
            count+=1
    end = time.time()
    single_query_time = end - start #Record the time taken for a single query
    return count, single_query_time

#This is the same save_results except it is used to see the time taken for each individual query in sequential search
def save_results_and_time(results, query_times, output_file):
    with open(output_file, 'w') as dataset:
        for i in range(len(results)):
            dataset.write(str(results[i]) + ", " + str(query_times[i]) + "\n")
    dataset.close()