import numpy as np

def parseFile(filename):#function to parse our file
    f = open(filename, "r")
    first = f.readline()
    first = first.strip("\n")
    data = first.split(" ")
    stops = int(data[0])
    rows = int(data[1])
    cols = int(data[2])

    transportationMatrix = np.zeros((stops, stops), dtype=np.integer)

    for line in f.readlines():
        line = line.strip("\n")
        data = line.split(" ", 3)
        start = int(data[0]) - 1
        end = int(data[1]) - 1
        number = int(data[2])
        transportationMatrix[start][end] = number

    return (stops, rows, cols, transportationMatrix)

def findFillCoordinate(hold, num):#function to find the optimal location to place a box

    for i in range(1, hold.shape[0]):#loop that returns in the case that there is a box of greater than or lesser value to place it on
        for j in range(0, hold.shape[1]):
            if hold[i][j] >= num and hold[i-1][j] == 0:
                return (j, i - 1)

    for i in range(0, hold.shape[1]):#loop that returns in the case that there is an empty column to stack in
        if hold[hold.shape[0] - 1][i] == 0:
            return (i, hold.shape[0] - 1)

    best = -1
    coord = (0,0)
    for i in reversed(range(0, hold.shape[0])):#returns if you have to place a box on top of a lower numbered box
        for j in range(0, hold.shape[1]):
            if hold[i][j] == 0:
                if (best == -1 or hold[i+1][j] < best) and hold[i+1][j] != 0:
                    best = hold[i+1][j]
                    coord = (j, i)
    return coord

def packContainers(stops, rows, cols, matrix):

    cost = 0
    cargoHold = np.zeros((rows, cols), dtype=np.integer)

    for i in range(1, stops + 1):#loop over all stops
        print("Leaving {}".format(i))
        moved = np.zeros(stops - 1)#array to store things that get taken out and have to be put back in

        for j in reversed(range(0, cargoHold.shape[0])): #nested loop to remove packages that are for this destination and to move things
            for k in range(0, cargoHold.shape[1]):

                if cargoHold[j][k] == i:#if theres a package for this stop
                    for y in reversed(range(0, j + 1)):#loop up to remove packages that may be stacked over a package for this stop
                        if cargoHold[y][k] != i and cargoHold[y][k] != 0:#if its not the same numbered box and not an empty slot
                            moved[i - 1] += 1
                            cost += 1
                            print("A cost was incurred at {},{}".format(k,y))
                        cargoHold[y][k] = 0

        print(cargoHold)#print the holds contents after removal

        for n in reversed(range(i, matrix.shape[1])): #loop to fill the ship with packages from this destination
            numToFill = matrix[i - 1][n] + moved[n - 1]
            print("Filling {0} things for dest {1}".format(numToFill, n + 1))
            currentCoord = findFillCoordinate(cargoHold, n + 1)#call method that finds the optimal coordinate to place the next box at

            while numToFill > 0:#fill the hold while theres boxes of this type to fill
                cargoHold[currentCoord[1]][currentCoord[0]] = n + 1
                currentCoord = findFillCoordinate(cargoHold, n + 1)
                numToFill -= 1
            print(cargoHold)

    return cost


args = parseFile("data1.dat")
print(args)
print("The cost for this trip is {}".format(packContainers(args[0], args[1], args[2], args[3])))
