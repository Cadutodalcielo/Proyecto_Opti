
# #R15: Después de salir de cada punto limpio p, el camión i debe recolectar la primera casa j del recorrido: 
m.addConstrs(sum(u[i,j,t,p] for j in J_) == 1 for i in I_ for t in T_ for p in P_)

#R16: Antes de llegar a un punto limpio p, el camión i debe recolectar la última casa j del recorrido:
m.addConstrs(sum(t_1[i,j,t,p] for j in J_) == 1 for i in I_ for t in T_ for p in P_)
