# -*- coding: utf-8 -*-
"""
Created on Sat Dec 09 11:58:59 2017

@author: Team 1-01
"""

from gurobipy import *
import MySQLdb as MySQL
db = MySQL.connect(user = 'root', passwd = 'root', host = 'localhost', db = 'nasdaq')

cur = db.cursor()

cur.execute('select * from cov')
Q = cur.fetchall()

Q_dict = {}
for i in range(len(Q)):
    Q_dict[(Q[i][0], Q[i][1])] = Q[i][2]
    
cur.execute('select * from r')
r = cur.fetchall()

stock_name = []
for i in range(len(r)):
    stock_name.append(Q[i][0])

m = Model("portfolio")
m.ModelSense = GRB.MAXIMIZE
m.setParam('Timelimit', 7200)

# Set up decision variables
a = []
for i in range(len(r)):
    a.append(m.addVar(vtype = GRB.CONTINUOUS, name = str(i), lb = 0.0))
m.update()

# Set objective function
m.setObjective(quicksum(r[i][1] * a[i] for i in range(len(a))), GRB.MAXIMIZE)
m.update()

# Set up constraints
risk_max = 0.01
increase = 0.01
for i in range(50):
    m.addConstr(quicksum((a[i]*Q_dict[(stock_name[i], stock_name[j])]*a[j] for i in range(len(a)) for j in range(len(a)))), 
                GRB.LESS_EQUAL, risk_max)
    m.addConstr(quicksum(a), GRB.EQUAL, 1.0)
    risk_max = risk_max + increase
    m.update()


    # Optimize the model
    m.optimize()
    
    cur.execute('insert into portfolio values (%s, %s)', (m.objVal, risk_max))
    db.commit() 
    m.remove(m.getQConstrs())