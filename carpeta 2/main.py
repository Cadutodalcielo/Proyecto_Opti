from gurobipy import Model, GRB, quicksum
import random

random.seed(10)

I = 40 # numero de camiones usados
G = 1715# Casas en la comuna
T = 7 # número de dias t
M = 80 # número máximo de recolectores m
N = 40 # número máximo de conductores n
P = 5 # número máximo de puntos limpios p


#Conjuntos
I_ = range(1, I + 1) # rango de camiones i
J_ = range(1, G + 1) # rango de casas j
T_ = range(1, T + 1) # rango de dias t
M_ = range(1, M + 1) # rango de recolectores m
N_ = range(1, N + 1) # rango de conductores n
P_ = range(1, P + 1) # rango de puntos limpios p


#Parametros
A =  40 # Número máximo de camiones i
B = {(i): random.randint(17000,19000) for i in I_} #capacidad máxima del camión i en kg: 18000
H = {(p): random.randint(1200000, 1300000) for p in P_ } #Capacidad punto limpio p: 1300 toneladas
C = 19990 # Precio de un basurero de reciclaje por unidad en pesos: $19990
Sn = {(n,t): random.randint(24000,25000) for n in N_ for t in T_} #Sueldo de cada conductor en en pesos: $24500
Sm = {(m,t): random.randint(14000,15000) for m in M_ for t in T_} #Sueldo de cada recolector m en pesos: $14600
f = 9.05 # Costo promedio de viajar entre casas  en pesos: $9.05
fj = {(j,p): random.randint(1000,2000) for j in J_ for p in P_} # Costo de viajar entre la casa j y el punto limpio p
E = random.randint(0,25) # kg de residuos reciclables por basurero (1 basurero por casa): 93 L de capacidad (peso calculado con su densidad)
#G = 171511 casas en la comuna (puente alto) ---> esta definido arriba
Lm = {(m,t): random.randint(4,7) for m in M_ for t in T_} #Implementos usados por el recolector m en el dia t
Ln = {(n,t): random.randint(4,7) for n in N_ for t in T_} #Implementos usados por el conductor n en el dia t
O = random.randint(30, 9000) # Costos de implementos de tabajadores 



#### ESCRIBA SU MODELO AQUI ####
m = Model()

#Variables
x = m.addVars(I_,T_, vtype = GRB.BINARY)
y = m.addVars(I_,J_,T_, vtype = GRB.BINARY)
w = m.addVars(M_,T_, vtype = GRB.BINARY)
z = m.addVars(N_,T_, vtype = GRB.BINARY)
v = m.addVars(I_,J_,T_, vtype = GRB.BINARY)
u = m.addVars(I_,J_,T_,P_, vtype = GRB.BINARY)
t_1 = m.addVars(I_,J_,T_,P_, vtype = GRB.BINARY)
r = m.addVars(J_, vtype = GRB.BINARY)
q = m.addVars(I_,T_,P_)




m.update()

#Función Objetivo

objetivo = sum(\
                sum(sum(sum(u[i,j,t,p]*fj[j,p] + t_1[i,j,t,p]*fj[j,p] for p in P_) +  v[i,j,t]*f for j in J_) for i in I_) + \
                    sum(w[m,t]*(Sm[m,t] + O*Lm[m,t]) for m in M_) + \
                        sum(z[n,t]*(Sn[n,t] + O*Ln[n,t]) for n in N_) \
                            for t in T_)           
m.setObjective(objetivo, GRB.MINIMIZE)

#R1: No se puede exceder el máximo de camiones disponibles.
m.addConstrs(sum(x[i,t] for i in I_) <= A for t in T_)


#R2: No superar la carga máxima del camión, si pasa por un punto limpio se puede volver a llenar.
m.addConstrs(sum(y[i,j,t] * E for j in J_) <= B[i]*(1 + sum(q[i,t,p] for p in P_)) for t in T_ for i in I_)

#R3: Los camiones deben recolectar todas las casas en la semana. lo hace insatisfacible 
m.addConstr(sum(sum(sum(y[i,j,t] for j in J_)for i in I_)for t in T_) == G)       

# #R4:Para que no se repitan, no puede pasar mas de un camión por la misma casa mas de una vez por semana.
# m.addConstrs(sum(y[i,j,t] for t in T_) == 1 - sum(y[a,j,t] for t in T_) for j in J_ for i in I_ for a in I_ if i != a)

#R5: Para cada camión deben haber al menos 1 conductor y 2 recolectores.
m.addConstrs(sum(z[n,t] for n in N_) >=  sum(x[i,t] for i in I_) for t in T_ )

#R6: Para cada camión deben haber al menos 1 conductor y 2 recolectores.
m.addConstrs(sum(w[m,t] for m in M_) >=  2*sum(x[i,t] for i in I_) for t in T_ )

#R6: Para cumplir con las jornadas laborales de conductores y recolectores, no se recolectan casas los Domingos.
m.addConstrs(x[i,7] == 0 for i in I_)

#R7: La cantidad de residuos recolectado debe ser menor a la capacidad del punto limpio.
m.addConstr(sum(sum(sum(y[i,j,t] * E for j in J_)for i in I_)for t in T_) <= sum(H[p] for p in P_)) 

#R8: Se deben comprar un basurero de reciclaje por casa para poder llevar a cabo la recolección
m.addConstr(sum(r[j] for j in J_) == G)


#R9: Los implementos usados por los conductores el dia t deben ser suficientes para cada trabajador.
m.addConstrs(sum(z[n,t] for n in N_) <= sum(Ln[n,t] for n in N_) for t in T_) 

#R10: Los implementos usados por los recolectores el dia t deben ser suficientes para cada trabajador.
m.addConstrs(sum(w[m,t] for m in M_) <= sum(Lm[m,t] for m in M_) for t in T_) 


#R11: Para poder pasar por las casas el camión i debe estar funcionando.
m.addConstrs(y[i,j,t] <= x[i,t] for i in I_ for j in J_ for t in T_)

#R12: Para poder pasar por una casa después de la casa j, el camión debe pasar primero por j.
m.addConstrs(v[i,j,t] <= y[i,j,t] for i in I_ for j in J_ for t in T_)

#R13: Para que j pueda ser la primera casa de ese dia t y despues de pasar por el punto p, el camion debe pasar por j ese dia.
m.addConstrs(u[i,j,t,p] <= y[i,j,t] for i in I_ for j in J_ for t in T_ for p in P_)

#R14: Para que j pueda ser la ultima casa de ese dia ty antes de pasar por el punto limpio p el camion debe pasar por j ese dia.
m.addConstrs(t_1[i,j,t,p] <= y[i,j,t] for i in I_ for j in J_ for t in T_ for p in P_)

# # #R15: Después de salir de cada punto limpio p, el camión i debe recolectar la primera casa j del recorrido: 
# m.addConstrs(sum(u[i,j,t,p] for j in J_) == 1 for i in I_ for t in T_ for p in P_)

# #R16: Antes de llegar a un punto limpio p, el camión i debe recolectar la última casa j del recorrido:
# m.addConstrs(sum(t_1[i,j,t,p] for j in J_) == 1 for i in I_ for t in T_ for p in P_)



m.update()
m.optimize()

#Imprimir Valor Objetivo

#################################

print("\n"+"-"*10+" Manejo Soluciones "+"-"*10)
print(f"El valor objetivo (con datos reales) es de: {m.ObjVal}")