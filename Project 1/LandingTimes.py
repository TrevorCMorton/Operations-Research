
# These three lines are required.  DO NOT REMOVE

from __future__ import division
from pyomo.environ import *
from pyomo.opt import *

# Instantiate and name the model

model = AbstractModel()
model.name = "Landing Times"

# Define Sets which are read from data file

model.PlaneNumber = Set()

# Parameters whose values are read from data file

model.MinTime = Param(model.PlaneNumber)
model.TargetTime = Param(model.PlaneNumber)
model.MaxTime = Param(model.PlaneNumber)
model.EarlyCost = Param(model.PlaneNumber)
model.LateCost = Param(model.PlaneNumber)
model.SameDifference = Param(model.PlaneNumber, model.PlaneNumber)
model.DiffDifference = Param(model.PlaneNumber, model.PlaneNumber)

# Define Variables

model.LandingTime = Var(model.PlaneNumber, within=NonNegativeReals)
model.IsEarly = Var(model.PlaneNumber, within=Binary)
model.IsLate = Var(model.PlaneNumber, within=Binary)
model.PrecedesSame = Var(model.PlaneNumber, model.PlaneNumber, within=Binary)
model.PrecedesDifferent = Var(model.PlaneNumber, model.PlaneNumber, within=Binary)
model.FirstOrLast = Var(model.PlaneNumber, within=Binary)

# Define Objective function
# To do this, define the actual function then place it into the model
# Here "M" represents general model

def CalcObjective(M):
    return sum(M.IsEarly[i] * M.EarlyCost[i] + M.IsLate[i] * M.LateCost[i] for i in M.PlaneNumber)

model.ObjFunction = Objective(rule=CalcObjective, sense=minimize)


# Constraints

# Ensures a plane can only be early, late or neither
def EnsureBinarySum(M, j):
    return M.IsEarly[j] + M.IsLate[j] <= 1

model.BinarySum = Constraint(model.PlaneNumber, rule=EnsureBinarySum)

# Ensures that there are 2 planes that are first or last
def EnsureFirstOrLast(M):
    return sum(M.FirstOrLast[i] for i in M.PlaneNumber) == 2

model.EnsureFirstLast = Constraint(rule=EnsureFirstOrLast)

# Ensures the upper bound on the landing time.  This bound is variable based on whether a plane is late, early or neither
def LandingUpper(M, i):
    return M.MaxTime[i] - (1 - M.IsLate[i]) * (M.MaxTime[i] - M.TargetTime[i]) - M.IsEarly[i] >= M.LandingTime[i]

model.LandingUpperBound = Constraint(model.PlaneNumber, rule=LandingUpper)

# Ensures the lower bound on the landing time.  This bound is variable based on whether a plane is late, early or neither
def LandingLower(M, i):
    return M.MinTime[i] + (1 - M.IsEarly[i]) * (M.TargetTime[i] - M.MinTime[i]) + M.IsLate[i] <= M.LandingTime[i]

model.LandingLowerBound = Constraint(model.PlaneNumber, rule=LandingLower)

# Ensures that for a given plane a plane either lands before it, after it, or it is the first or last plane
def EnsureSameDiffCount(M, i):
    return M.FirstOrLast[i] + sum(M.PrecedesSame[i, j] + M.PrecedesSame[j, i] + M.PrecedesDifferent[i, j] + M.PrecedesDifferent[j, i] for j in M.PlaneNumber) == 2

model.SameDiffCount = Constraint(model.PlaneNumber, rule=EnsureSameDiffCount)

# Ensures that each plane has at most one plane come directly before it
def Precedes1(M, j):
    return sum(M.PrecedesSame[i, j] + M.PrecedesDifferent[i, j] for i in M.PlaneNumber) <= 1

model.Pre1 = Constraint(model.PlaneNumber, rule=Precedes1)

# Ensures that each plane has at most one plane come directly after it
def Precedes2(M, i):
    return sum(M.PrecedesSame[i, j] + M.PrecedesDifferent[i, j] for j in M.PlaneNumber) <= 1

model.Pre2 = Constraint(model.PlaneNumber, rule=Precedes2)

# Ensures a plane can't procede itself
def MiddleDiagZeroSame(M, i):
    return M.PrecedesSame[i, i] == 0

model.MidZeroSame = Constraint(model.PlaneNumber, rule=MiddleDiagZeroSame)

# Same as above constraint
def MiddleDiagZeroDiff(M, i):
    return M.PrecedesDifferent[i, i] == 0

model.MidZeroDiff = Constraint(model.PlaneNumber, rule=MiddleDiagZeroDiff)

# Ensures that planes are forced to wait the given amount of time after the plane before lands on the same runway
def LandingOrder1(M, i, j):
    return M.LandingTime[j] >= M.LandingTime[i] - 500 * (1 - M.PrecedesSame[i, j]) + M.PrecedesSame[i, j] * M.SameDifference[i, j]

model.Landing1 = Constraint(model.PlaneNumber, model.PlaneNumber, rule=LandingOrder1)

# Same as above, but this time for planes on different runways
def LandingOrder2(M, i, j):
    return M.LandingTime[j] >= M.LandingTime[i] - 500 * (1 - M.PrecedesDifferent[i, j]) + M.PrecedesDifferent[i, j] * M.DiffDifference[i, j]

model.Landing2 = Constraint(model.PlaneNumber, model.PlaneNumber, rule=LandingOrder2)


# Create a problem instance
instance = model.create_instance("LandingTimes.dat")

# Indicate which solver to use
# Opt = SolverFactory("gurobi", solver_io="python")
Opt = SolverFactory("glpk")

# Generate a solution
Soln = Opt.solve(instance)

# Load solution to instance then Display the solution
instance.solutions.load_from(Soln)
display(instance)