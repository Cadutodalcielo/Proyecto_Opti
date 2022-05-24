m.addConstrs(sum(u[i,j,t,p] for j in J_) == 1 for i in I_ for t in T_ for p in P_)
