import time
import tqdm
from R_tree import RTree
from util import load_data_points, load_queries, save_results, sequential_scan, save_results_and_time

def main():
    #read the 150,000 data points and the 200 query rectangles and store the data in a list
    points_file = "data_points.txt"
    points = load_data_points(points_file)

    queries_file = "200_range_queries.txt"
    queries = load_queries(queries_file)

    #Sequential Scanning
    sequential_results = []
    query_times = []
    print("Scanning sequentially: Please wait...\n")
    for query in tqdm.tqdm(queries): #loop though queries
        count, query_time = sequential_scan(points, query) #get the number of points in a query rectangle and the time taken to run that query
        sequential_results.append(count) #Store a list of results
        query_times.append(query_time) #Store a list of time taken for each query to complete

    save_results(sequential_results, "sequential_scan_results.txt") #save results used to output the results in text file
    save_results_and_time(sequential_results, query_times, "sequential_scan_results_and_time.txt") #This outputs the result as well as the time taken for each query
    #print total and average time of sequential scan queries
    sum = 0
    for qt in query_times:
        sum += qt
    print("Total time taken: ", sum)
    print("Average query time: ", sum / len(query_times))

    # build R-Tree
    rtree = RTree()

    #R_Tree_start takes the time just before you start inserting the data points into the Rtree
    #R_Tree_end takes the time after you finished inserting all the data points into the Rtree
    #Used_time is the difference between these two values which equals the time it takes to insert all the data points and construct the Rtree
    print("Building the R-Tree: Please wait...\n")
    R_Tree_start=time.time()

    #tqdm used to show progression bar. Provides a visual way of showing how long it will take to finish running this for loop
    for point in tqdm.tqdm(points): #insert data points from the root one by one 
        rtree.insert(rtree.root, point)

    R_Tree_end=time.time()
    Used_time=R_Tree_end-R_Tree_start
    print("R-Tree construction completed\n")
    print("The time-cost of building up the R-Tree is",Used_time,"seconds.\n")

    #The code above is used to show time taken to construct Rtree
    #The same approach is used below to record the time taken to see how long it takes to query 
    rtree_results = []
    Answer_query_start=time.time()
    for query in queries:
        rtree_results.append(rtree.query(rtree.root, query))
    Answer_query_end=time.time()
    Query_processing_time=Answer_query_end-Answer_query_start

    print("There are",rtree_results,"data points included in the query.\n")
    print("The query processing time is",Query_processing_time,"seconds.")

    save_results(rtree_results, "rtree_results.txt")

    for i in range(len(rtree_results)): #Loop 200 times (total number of queries) and compare the results from rtree and sequential search
        if rtree_results[i] != sequential_results[i]:  #The results should be the same so the program shouldn't print any mismatches
            print("Mismatch of rtree and sequential scan results at query ", i)


if __name__ == '__main__':
    main()