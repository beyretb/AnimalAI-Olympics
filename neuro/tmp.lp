
timestep(0..1).
% Observables rules
present(X,T):- visible(X, _, T).
visible(T):- visible(X, _, T).
not_occluding(X, T):-on(agent, X, T).
separator(Y, T):-on(agent, X, T), adjacent(X, Y, T), platform(X).
occludes(X,Y,T) :- present(Y, T), visible(X, _, T), not visible(Y, _, T), not separator(X, T), not not_occluding(X, T).

% Observables - > actions: this is what we need to learn
:- initiate(explore(X1,Y,_), T), initiate(explore(X2,Y,_), T), X1 != X2.
:~initiate(explore(X,Y,Z),T).[Z@1,X,Z]

% Completion checks checks
check(visible(Y),T):- initiate(explore(X,Y,Z),T).
check(time, T):- initiate(explore(X,Y,Z),T).
check(time, T):- initiate(interact(X),T).
check(time, T):- initiate(rotate,T).
#modeh(1, initiate(explore(var(V0),var(V1),var(V2)),var(T))).
#modeh(1, initiate(interact(var(V0)),var(T))).
#modeh(1, initiate(rotate,var(T))).
#maxv(4).

#modeb(1, goal(var(X))).
#modeb(1, visible(var(X), var(Z), var(T))).
#modeb(1, visible(var(T))).
#modeb(1, occludes(var(X),var(Y), var(T))).
#modeb(1, timestep(var(T))).
#pos(a1@1,{initiate(interact(0),0)}, {}, {visible(0,5,0).
goal(0).
}).
#pos(a2@2,{initiate(interact(0),0)}, {}, {visible(0,5,0).
goal(0).
}).
#pos(a3@3,{initiate(rotate,0),initiate(rotate,1),initiate(interact(0),2)}, {}, {visible(0,5,0).
goal(0).

visible(0,5,1).
goal(0).

visible(0,6,2).
goal(0).
}).
#pos(a4@4,{initiate(interact(0),0)}, {}, {visible(0,5,0).
goal(0).
}).
#pos(a5@5,{initiate(rotate,0),initiate(interact(0),1)}, {}, {visible(0,5,0).
goal(0).

visible(0,5,1).
goal(0).
}).
#pos(a6@6,{initiate(interact(0),0)}, {}, {visible(0,5,0).
goal(0).
}).
#pos(a7@7,{initiate(rotate,0),initiate(interact(0),1)}, {}, {visible(0,5,0).
goal(0).

visible(0,5,1).
goal(0).
}).
#pos(a8@8,{initiate(interact(0),0)}, {}, {visible(0,5,0).
goal(0).
}).
#pos(a9@9,{initiate(interact(0),0)}, {}, {visible(0,5,0).
goal(0).
}).
#pos(a10@10,{initiate(interact(0),0)}, {}, {visible(0,5,0).
goal(0).
}).
#pos(a11@11,{initiate(interact(0),0)}, {}, {visible(0,5,0).
goal(0).
}).
#pos(a12@12,{initiate(interact(0),0)}, {}, {visible(0,5,0).
goal(0).
}).
#pos(a13@13,{initiate(interact(0),0)}, {}, {visible(0,5,0).
goal(0).
}).
#pos(a14@14,{initiate(rotate,0),initiate(interact(0),1)}, {}, {visible(0,5,0).
goal(0).

visible(0,5,1).
goal(0).
}).
#pos(a15@15,{initiate(interact(0),0)}, {}, {visible(0,5,0).
goal(0).
}).
#pos(a16@16,{initiate(rotate,0),initiate(rotate,1),initiate(interact(0),2)}, {}, {visible(0,5,0).
goal(0).

visible(0,5,1).
goal(0).

visible(0,6,2).
goal(0).
}).
#pos(a17@17,{initiate(rotate,0),initiate(interact(0),1)}, {}, {visible(0,5,0).
goal(0).

visible(0,5,1).
goal(0).
}).
#pos(a18@18,{initiate(interact(0),0)}, {}, {visible(0,5,0).
goal(0).
}).
