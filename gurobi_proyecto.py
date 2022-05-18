from gurobipy import Model, GRB, quicksum
import random

random.seed(10)
I = 5 # número máximo de camiones i
J = 20 # número máximo de casas j
T = 7 # número de dias t
M = 10 # número máximo de recolectores m
N = 5 # número máximo de conductores n
P = 2 # número máximo de puntos limpios p


#rangos
I_ = range(1, I + 1) # rango de camiones i
J_ = range(1, J + 1) # rango de casas j
T_ = range(1, T + 1) # rango de dias t
M_ = range(1, M + 1) # rango de recolectores m
N_ = range(1, N + 1) # rango de conductores n
P_ = range(1, P + 1) # rango de puntos limpios p


#Conjuntos: Hay que definir los párametros (Falta revisar los rangos de los randint)
A = random.choices(N_, k=int(n*0.2)) # Número máximo de camiones i ->REVISAR: no se como definirlo
B = {(i): random.randint(15000, 40000) for i in I_} #capacidad máxima del camión i
H = {(p): random.randint(5000, 10000) for p in P_ }
C = random.choices(N_, k=int(n*0.2)) # Precio de un basurero de reciclaje ->REVISAR: no se como definirlo
Sn = {(n,t): random.randint(9,12) for n in N_ for t in T_} #Sueldo de cada conductor n
Sm = {(m,t): random.randint(9,12) for m in M_ for t in T_} #Sueldo de cada recolector m
f = random.choices(N_, k=int(n*0.2)) # Costo promedio de viajar entre casas ->REVISAR: no se como definirlo
fj = {(j,p): random.randint(9,12) for j in J_ for p in P_} # Cpsto de viajar entre la casa j y el punto limpio p
E = random.choices(N_, k=int(n*0.2)) # kg de residuos reciclables por basurero (1 basurero por casa) ->REVISAR: no se como definirlo
G = random.choices(N_, k=int(n*0.2)) # Casas en la comuna ->REVISAR: no se como definirlo
Lm = {(m,t): random.randint(9,12) for m in M_ for t in T_} #Implementos usados por el recolector m en el dia t
Ln = {(n,t): random.randint(9,12) for n in N_ for t in T_} #Implementos usados por el conductor n en el dia t
O = random.choices(N_, k=int(n*0.2)) # Costos de implementos de tabajadores ->REVISAR: no se como definirlo








#### ESCRIBA SU MODELO AQUI ####
m = Model()

#Variables
x = m.addVars(I_,T_, vtype = GRB.BINARY)
y = m.addVars(I_,J_,T_, vtype = GRB.BINARY)
w = m.addVars(M_,T_, vtype = GRB.BINARY)
z = m.addVars(N_,T_, vtype = GRB.BINARY)
v = m.addVars(I_,J_,T_, vtype = GRB.BINARY)
u = m.addVars(I_,J_,T_, vtype = GRB.BINARY)
t = m.addVars(I_,J_,T_, vtype = GRB.BINARY)
r = m.addVars(J_, vtype = GRB.BINARY)
q = m.addVars(I_,T_,P_)




m.update()

#Función Objetivo
objetivo = sum(sum(sum(v[i,j,t]for e in range(1,exp[i]+1))for k in K_)for i in N_) + \
            sum(sum(sum(G[p] * r[p,e] for e in range(1,exp[p]+1))for p in P)for k in K_) - \
            sum(sum(sum(sum(C[i,k] * y[i,j,h,k] + S * x[i,j,h,k] for h in D_)for j in J_)for k in K_)for i in N_)
m.setObjective(objetivo, GRB.MINIMIZE)

#R1: No se puede exceder el máximo de camiones disponibles.
m.addConstrs(sum(x[i,t] for i in I_) <= A for t in T_)


#R2: No superar la carga máxima del camión, si pasa por un punto limpio se puede volver a llenar.
m.addConstrs(sum(y[i,j,t] for j in J_) <= B[i]*(1 + sum(q[i,t,p] for p in P_)) for t in T_ for i in I_)

#R3: Los camiones deben recolectar todas las casas en la semana.
m.addConstrs(sum(sum(sum(y[i,j,t] for j in J)for i in I_)for t in T_) == G )

#R4:Para que no se repitan, no puede pasar mas de un camión por la misma casa mas de una vez por semana.
# REVISAR: Como aplicar el subconjunto alpha(que se usa para que el valor de i no se repita).
m.addConstrs()

#R5: Para cada camión deben haber al menos 1 conductor y 2 recolectores.
m.addConstrs(sum(z[n,t] for n in N_) + 2 * sum(w[m,t] for m in M_) >= 3 * sum(x[i,t] for i in I_) for t in T_)

#R6: Para cumplir con las jornadas laborales de conductores y recolectores, no se recolectan casas los Domingos.
m.addConstrs(x[i,7] == 0 for i in I_)

#R7: La cantidad de residuos recolectado debe ser menor a la capacidad del punto limpio.
m.addConstrs(sum(sum(sum(y[i,j,t] * E for j in J_)for i in I_)for t in T_) <= sum(H[p] for p in P_)) 

#R8: Se debe comprar un basurero de reciclaje por casa para poder llevar a cabo la recolección
m.addConstrs(sum(r[j] for j in J_) == G)


#R9: Los implementos usados por los conductores el dia t deben ser suficientes para cada trabajador.
m.addConstrs(sum(z[n,t] for n in N_) <= sum(Ln[n,t] for n in N_) for t in T_) 

#R10: Los implementos usados por los recolectores el dia t deben ser suficientes para cada trabajador.
m.addConstrs(sum(w[m,t] for m in M_) <= sum(Lm[m,t] for m in M_) for t in T_) 


#R11: Para poder pasar por las casas el camión i debe estar funcionando.
m.addConstrs(y[i,j,t] <= x[i,t] for i in I_ for j in J_ for t in T_)

#R12: Para poder pasar por una casa después de la casa j, el camión debe pasar primero por j.
m.addConstrs(v[i,j,t] <= y[i,j,t] for i in I_ for j in J_ for t in T_)

#R13: Para que j pueda ser la primera casa de ese dia t, el camion debe pasar por j ese dia.
m.addConstrs(u[i,j,t] <= y[i,j,t] for i in I_ for j in J_ for t in T_)

#R14: Para que j pueda ser la ultima casa de ese dia t, el camion debe pasar por j ese dia.
m.addConstrs(t[i,j,t] <= y[i,j,t] for i in I_ for j in J_ for t in T_)



m.update()
m.optimize()

#Imprimir Valor Objetivo

#################################

print("\n"+"-"*10+" Manejo Soluciones "+"-"*10)
print(f"El valor objetivo es de: {m.ObjVal}")