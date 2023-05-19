from sat_solvers import *

clauses = []
literals = []

with open('example_clauses.txt', 'r') as f:
  for line in f:
    clause = []
    for lit in line.strip().split('+'):
      literal = lit.strip('!')
      if literal not in literals: 
        literals.append(literal)
      clause.append((literal, lit[0]=='!'))
    clauses.append(clause)


print_boolean_func(clauses)
print("Literals: ", literals)

#print_boolean_func(propagate_assignment(clauses, 'a', True)[0])
print("Solving:")

print("Solutions: ", sat_dp_conflict([], clauses, (clauses, False, False), {}, literals))

print_boolean_func(clauses)