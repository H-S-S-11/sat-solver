from copy import deepcopy


def print_boolean_func(clauses):
  to_print = ""
  for clause in clauses:
    to_print += '('
    for lit in clause:
      if lit[1]: to_print += '!'
      to_print += f"{lit[0]}+"
    to_print = to_print.strip('+') + ')'
  print(to_print)

def propagate_assignment(func, variable, assignment):
  # Remove any literals equal to zero from clauses
  # Remove any clauses equal to one from the function
  new_func = []
  # If there are empty clauses, cannot reach SAT
  empty_clauses = False
  for clause in func:
    new_clause = []
    clause_sat = False
    for lit in clause:
      if lit[0] != variable:
        new_clause.append(lit)
      else:
        # Propagate the assignment
        if assignment ^ lit[1]:
          # assigned 1 and not inverted, or assigned 0 and inverted
          clause_sat = True
        else:
          pass
    
    if not clause_sat:
      new_func.append(new_clause)
      if (len(new_clause)==0):
        empty_clauses = True 

  return new_func, empty_clauses
  
def propagate_assignment_conflicts(original_func, func, variable, assignment, assignments):
  # Remove any literals equal to zero from clauses
  # Remove any clauses equal to one from the function
  new_func = []
  implied_assignments={}
  # If there are empty clauses, cannot reach SAT
  empty_clauses = False
  func_sat = True
  for i in range(0, len(func)):
    clause = func[i]
    new_clause = []
    clause_sat = (clause[0][0]=='1')

    for lit in clause:
      if lit[0] != variable:
        new_clause.append(lit)
      else:
        # Propagate the assignment
        if assignment ^ lit[1]:
          # assigned 1 and not inverted, or assigned 0 and inverted
          clause_sat = True
          break
        else:
          pass
    
    if not clause_sat:
      new_func.append(new_clause)
      func_sat = False
      if len(new_clause) == 1:
        # if only a single literal imply that it will be 1
        implied_lit, implied_assign = new_clause[0][0], not new_clause[0][1] 
        #print(f"Implying {implied_lit} = {implied_assign}")
        # This bit is dead code, shouldn't be possible to get here
        if (implied_lit in assignments.keys()):
          raise NotImplementedError
          if assignments[implied_lit] != implied_assign:
            print("CONFLICT")
            return
        elif (implied_lit in implied_assignments.keys()):
          if implied_assignments[implied_lit][0] != implied_assign:
            print(f"CONFLICT for literal {implied_lit} in clauses {implied_assignments[implied_lit][1]} and {i} with assignments ", assignments)
            conflict_clause = {}
            for item in (original_func[implied_assignments[implied_lit][1]] + original_func[i]):
              if item[0] != implied_lit:
                conflict_clause[item[0]] = item[1]
            # Should have used OrderedDicts
            conflict = []
            for key, value in conflict_clause.items():
              conflict.append((key, value))
            print("Adding conflict clause: ")
            print_boolean_func([conflict])
            original_func.append(conflict)
            # We know the conflict clause has failed
            new_func.append([])
            return new_func, True, False, implied_assignments
        else:
          implied_assignments[implied_lit] = (implied_assign, i)

      if (len(new_clause)==0):
        empty_clauses = True
    else:
      new_func.append([('1', False)])
  print("Implied: ", implied_assignments)
  # Propagate the implied assignments
  merged_assign = deepcopy(assignments)
  for var, assign in implied_assignments.items():
    new_func, empty_clauses, func_sat, new_implied = propagate_assignment_conflicts(original_func, new_func, var, assign[0], merged_assign)
    merged_assign[var] = assign[0]
    for key, value in new_implied.items():
      implied_assignments[key] = value
  return new_func, empty_clauses, func_sat, implied_assignments

def sat_dp(propagated, assignments, literals):
  func, empty_clauses = propagated
  print("Current assignment:", assignments)
  print_boolean_func(func)
  if empty_clauses:
    print('NO SAT')
    return 'NO SAT'
  
  if len(func)==0:
    return assignments
  
  # Pick an unassigned literal
  to_assign = 'x'
  for lit in literals:
    if lit not in assignments.keys():
      to_assign = lit
      break
  new_assignments = deepcopy(assignments)

  new_assignments[to_assign] = False
  split_0 = sat_dp(propagate_assignment(func, to_assign, False), new_assignments, literals)
  if split_0 != 'NO SAT':
    return split_0
  else:
    new_assignments[to_assign] = True
    return sat_dp(propagate_assignment(func, to_assign, True), new_assignments, literals)

def sat_dp_conflict(solutions, original, propagated, assignments, literals):
  func, empty_clauses, func_sat = propagated
  print("Current assignment:", assignments)
  print_boolean_func(func)

  if empty_clauses:
    print('NO SAT')
    return 'NO SAT'
  
  if func_sat:
    solutions.append(assignments)
    print("SAT")
    return solutions
  
  # Pick an unassigned literal
  to_assign = 'x'
  for lit in literals:
    if lit not in assignments.keys():
      to_assign = lit
      break
  
  # Try assigning to 0
  new_assignments = deepcopy(assignments)
  new_assignments[to_assign] = False
  print(f"Trying {to_assign} = 0")
  new_func, empty_clauses, func_sat, implied_assignments = propagate_assignment_conflicts(original, func, to_assign, False, new_assignments)
  for var, assign in implied_assignments.items():
    new_assignments[var] = assign[0]
  split_0 = sat_dp_conflict(solutions, original, (new_func, empty_clauses, func_sat), new_assignments, literals)
  # Don't need these cause the append actually adds to original object
  #if split_0 != 'NO SAT':
  #  solutions += split_0
  

  # Try assigning to 1
  new_assignments = deepcopy(assignments)
  new_assignments[to_assign] = True
  print(f"Trying {to_assign} = 1")
  new_func, empty_clauses, func_sat, implied_assignments = propagate_assignment_conflicts(original, func, to_assign, True, new_assignments)
  for var, assign in implied_assignments.items():
    new_assignments[var] = assign[0]
  split_1 =  sat_dp_conflict(solutions, original, (new_func, empty_clauses, func_sat), new_assignments, literals)
  # Don't need these cause the append actually adds to original object
  #if split_1 != 'NO SAT':
  #  solutions += split_1
  
  return solutions
