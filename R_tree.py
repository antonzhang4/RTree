import sys
import math

#indicate the maximum number of elements/values in each node before splitting
B = 4

#nodes are essential for constructing RTree. The entry node or the top node is the root node
#Any insertion or search of data points must first start from the root node and go down
class Node(object): #node class
    def __init__(self):
        self.id = 0
        # for internal nodes
        self.child_nodes = []
        # for leaf nodes
        self.data_points = []
        self.parent = None
        self.MBR = {
            'x1': -1,
            'y1': -1,
            'x2': -1,
            'y2': -1,
        }
    #Calculate perimeter of MBR. This is needed when splitting MBRs to find the best split.
    #It is also used to choose the best nodes to traverse or insert new data points into
    def perimeter(self):
        # only calculate the half perimeter here
        #Calculating the full perimeter works but using half the perimeter works just fine
        return (self.MBR['x2'] - self.MBR['x1']) + (self.MBR['y2'] - self.MBR['y1'])

    #Checking if the number of data points in a leaf node or the number of MBRs in an internal or root node exceed B
    #This is done by checking the data_points list inside the node class for a leaf node
    #This is done by checking the child_nodes list inside the node class for other nodes.
    def is_overflow(self):
        if self.is_leaf():
            if self.data_points.__len__() > B: #Checking overflows of data points, B is the upper bound.
                return True
            else:
                return False
        else:
            if self.child_nodes.__len__() > B: #Checking overflows of child nodes, B is the upper bound.
                return True
            else:
                return False

    #Checking if the node you are currently at is a root node. This is done by checking if the node you are at has any parents
    #If it doesn't, then it is a root node
    def is_root(self):
        if self.parent is None:
            return True
        else:
            return False

    #Check if you are at a leaf node. If the number of child_nodes is 0, it is a leaf node
    def is_leaf(self):
        if self.child_nodes.__len__() == 0:
            return True
        else:
            return False

class RTree(object): #R tree class
    #Create a root
    #Must always start the RTree by creating a root node or entry point for insertion and searching
    def __init__(self):
        self.root = Node()
    
    #Called by main function. Main function will loop through each query in the range query dataset and call this function
    def query(self, node, query): #run to answer the query
        num = 0
        if node.is_leaf(): #check if a data point is included in a leaf node
            for point in node.data_points:
                if self.is_covered(point, query): #The is_covered function will let us know if there are any data points inside the query rectangle
                    num = num + 1
            return num  #num variable is number of data points found within a query
        else:
            for child in node.child_nodes: #If it is an MBR, check all the child nodes to see whether there is an interaction
                if self.is_intersect(child, query): #If there is an interaction, keep continue to check the child nodes in the next layer till the leaf nodes
                    num = num + self.query(child, query)
            return num
    
    #This function checks to see if the query rectangle covers any data points of the leaf node
    #This is done by ensuring that the x-coordinate of the data point lies between x1 and x2 of the MBR
    #Also the y coordinate of the data point lies between the y1 and y2 of the MBR
    def is_covered(self, point, query):
        x1, x2, y1, y2 = query['x1'], query['x2'], query['y1'], query['y2']
        if x1 <= point['x'] <= x2 and y1 <= point['y'] <= y2:
            return True
        else:
            return False    
    
    #This function is used to check intersection of MBRs with the query rectangle
    #The method involves taking the centre point, length and width of the current internal node and the query rectangle.
    #if the difference between the centre points of the MBR and the query rectangle in the x-direction is smaller than difference in lengths of the two rectangles
    #and the difference between the centre points of the MBR and the query rectangle in the y-direction is smaller than difference in widths of the two rectangles
    #then we can say that the two rectangles intersect. If they do intersect, you return true. You will know that you have to search through this internal node
    #if return they don't intersect, we return false and we know to ignore these internal nodes while searching
    def is_intersect(self, node, query):
        # if two mbrs are intersected, then:
        # |center1_x - center2_x| <= length1 / 2 + length2 / 2 and:
        # |center1_y - center2_y| <= width1 / 2 + width2 / 2
        center1_x = (node.MBR['x2'] + node.MBR['x1']) / 2
        center1_y = (node.MBR['y2'] + node.MBR['y1']) / 2
        length1 = node.MBR['x2'] - node.MBR['x1']
        width1 = node.MBR['y2'] - node.MBR['y1']
        center2_x = (query['x2'] + query['x1']) / 2
        center2_y = (query['y2'] + query['y1']) / 2
        length2 = query['x2'] - query['x1']
        width2 = query['y2'] - query['y1'] 
        if abs(center1_x - center2_x) <= length1 / 2 + length2 / 2 and\
                abs(center1_y - center2_y) <= width1 / 2 + width2 / 2:  #we check the absolute value
            return True
        else:
            return False  
    
    #This insertion function is called by the main function in main.py
    #In main.py, you call the Rtree class which will initialize and create a root node for the Rtree
    #Then you start inserting points into the RTree starting from the root node
    def insert(self, u, p): # insert p(data point) to u (MBR)
        if u.is_leaf(): #If you are at a leaf node
            self.add_data_point(u, p) #add the data point and update the corresponding MBR
            if u.is_overflow(): #If the node is overflowing
                self.handle_overflow(u) #handle overflow for leaf nodes
        else:   #If you aren't at a leaf node
            v = self.choose_subtree(u, p) #choose a subtree to insert the data point to miminize the perimeter sum
            self.insert(v, p) #keep continue to check the next layer recursively
            self.update_mbr(v) #update the MBR for inserting the data point

    #This function is used to decide which child nodes to enter. It is used in the insert function if you are at an internal or root node
    #choose_subtree uses the peri_increase function to find the child node that will have the least increase in perimeter sum when inserting this new point
    #Need to use this node because minimizing perimeter sums result in fewer overlaps of MBRs, leading to efficient RTree searching
    def choose_subtree(self, u, p): 
        if u.is_leaf(): #find the leaf and insert the data point
            return u
        else:
            min_increase = sys.maxsize #set an initial value
            best_child = None
            for child in u.child_nodes: #check each child to find the best node to insert the point 
                if min_increase > self.peri_increase(child, p):
                    min_increase = self.peri_increase(child, p)
                    best_child = child
            return best_child

    #This function will take in a child node from choose_subtree and calculate what the perimeter of the child node MBR will be after inserting the data point
    def peri_increase(self, node, p): # calculate the increase of the perimeter after inserting the new data point
        # new perimeter - original perimeter = increase of perimeter
        origin_mbr = node.MBR
        x1, x2, y1, y2 = origin_mbr['x1'], origin_mbr['x2'], origin_mbr['y1'], origin_mbr['y2']
        increase = (max([x1, x2, p['x']]) - min([x1, x2, p['x']]) +
                    max([y1, y2, p['y']]) - min([y1, y2, p['y']])) - node.perimeter()
        return increase

    #This function will first split the overflowing node into two. It then adjusts all nodes that have been affected by this split
    #The parents and child nodes of every node that is affected will be reassigned
    def handle_overflow(self, u):
        u1, u2 = self.split(u) #u1 u2 are the two splits returned by the function "split"
        # if u is root, create a new root with s1 and s2 as its' children
        if u.is_root():
            new_root = Node() #Initialize new root node
            self.add_child(new_root, u1) #Split nodes have new parents. The new root node's children is set to the split nodes
            self.add_child(new_root, u2)
            self.root = new_root #Set the value of the new root
            self.update_mbr(new_root) #Update the root node's MBR
        # if u is not root, delete u, and set s1 and s2 as u's parent's new children
        else:
            #Similar process as root node. Reset the child and parent nodes after splitting
            w = u.parent
            # copy the information of s1 into u
            w.child_nodes.remove(u)
            self.add_child(w, u1) #link the two splits and update the corresponding MBR
            self.add_child(w, u2)
            if w.is_overflow(): #check the parent node recursively. This is needed if the parent overflows after splitting
                self.handle_overflow(w)

    #This function splits a node into two. It is only splitting the node when it is overflowing.
    #It will loop through a sorted list of data points or MBRs (depending on leaf or internal node)
    #Inside this loop is another loop that checks a number of splits. It uses perimeter() function to decide which split is best
    def split(self, u):
        # split u into s1 and s2
        best_s1 = Node()
        best_s2 = Node()
        best_perimeter = sys.maxsize
        # u is a leaf node
        if u.is_leaf():
            m = u.data_points.__len__()
            # create two different kinds of divides
            divides = [sorted(u.data_points, key=lambda data_point: data_point['x']),
                       sorted(u.data_points, key=lambda data_point: data_point['y'])] #sorting the points based on X dimension and Y dimension
            for divide in divides:
                for i in range(math.ceil(0.4 * B), m - math.ceil(0.4 * B) + 1): #check the combinations to find a near-optimal one
                    s1 = Node() #Create a new node s1 for the 1st node of the split
                    s1.data_points = divide[0: i] #This node will store a certain number of data points depending on the split sizes
                    self.update_mbr(s1) #Store an MBR for this new node
                    s2 = Node() #Repeat process from s1 for s2
                    s2.data_points = divide[i: divide.__len__()]
                    self.update_mbr(s2)
                    if best_perimeter > s1.perimeter() + s2.perimeter():  #Only take the split with the smallest perimeter sum
                        best_perimeter = s1.perimeter() + s2.perimeter()
                        best_s1 = s1
                        best_s2 = s2
        # if u is a internal node
        #The process for splitting internal nodes is the same as leaf nodes
        else:
            # create four different kinds of divides
            m = u.child_nodes.__len__()
            divides = [sorted(u.child_nodes, key=lambda child_node: child_node.MBR['x1']), #sorting based on MBRs
                       sorted(u.child_nodes, key=lambda child_node: child_node.MBR['x2']),
                       sorted(u.child_nodes, key=lambda child_node: child_node.MBR['y1']),
                       sorted(u.child_nodes, key=lambda child_node: child_node.MBR['y2'])]
            for divide in divides:
                for i in range(math.ceil(0.4 * B), m - math.ceil(0.4 * B) + 1): #check the combinations
                    s1 = Node()
                    s1.child_nodes = divide[0: i]
                    self.update_mbr(s1)
                    s2 = Node()
                    s2.child_nodes = divide[i: divide.__len__()]
                    self.update_mbr(s2)
                    if best_perimeter > s1.perimeter() + s2.perimeter():
                        best_perimeter = s1.perimeter() + s2.perimeter()
                        best_s1 = s1
                        best_s2 = s2
        #All the child nodes of the split nodes must have their parent nodes reassigned
        for child in best_s1.child_nodes:
            child.parent = best_s1
        for child in best_s2.child_nodes:
            child.parent = best_s2

        return best_s1, best_s2

    #This function is used to reassign the children of the split nodes. The parents of the children of these nodes are reassigned after the split
    #MBRs for the split nodes are also recalculated after after the split
    def add_child(self, node, child):
        node.child_nodes.append(child) #add child nodes to the current parent (node) and update the MBRs. It is used in handeling overflows
        child.parent = node
        if child.MBR['x1'] < node.MBR['x1']:
            node.MBR['x1'] = child.MBR['x1']
        if child.MBR['x2'] > node.MBR['x2']:
            node.MBR['x2'] = child.MBR['x2']
        if child.MBR['y1'] < node.MBR['y1']:
            node.MBR['y1'] = child.MBR['y1']
        if child.MBR['y2'] > node.MBR['y2']:
            node.MBR['y2'] = child.MBR['y2']
    # return the child whose MBR requires the minimum increase in perimeter to cover p

    #This function is called by the insert function. It is used when you are at a leaf node to append the inserted data points into the data_points list of the leaf node
    def add_data_point(self, node, data_point): #add data points and update the the MBRS
        node.data_points.append(data_point)
        if data_point['x'] < node.MBR['x1']:
            node.MBR['x1'] = data_point['x']
        if data_point['x'] > node.MBR['x2']:
            node.MBR['x2'] = data_point['x']
        if data_point['y'] < node.MBR['y1']:
            node.MBR['y1'] = data_point['y']
        if data_point['y'] > node.MBR['y2']:
            node.MBR['y2'] = data_point['y']

    #Leaf nodes store actual data points and an MBR of those data points
    #Other nodes construct an MBR taking the MBRs of all their child nodes
    def update_mbr(self, node): #update MBRs when forming a new MBR. It is used in checking the combinations and update the root
        x_list = []
        y_list = []
        #If leaf node, store the x-coordinates in x_list and y-coordinates in y_list
        if node.is_leaf():
            x_list = [point['x'] for point in node.data_points]
            y_list = [point['y'] for point in node.data_points]
        #If internal node, store the x1-coordinates first and then the x2 coordinates are appended at the end of x_list. The same thing happens for y_list
        else:
            x_list = [child.MBR['x1'] for child in node.child_nodes] + [child.MBR['x2'] for child in node.child_nodes]
            y_list = [child.MBR['y1'] for child in node.child_nodes] + [child.MBR['y2'] for child in node.child_nodes]
        #Calculate and store the MBR
        new_mbr = {
            'x1': min(x_list),
            'x2': max(x_list),
            'y1': min(y_list),
            'y2': max(y_list)
        }
        node.MBR = new_mbr