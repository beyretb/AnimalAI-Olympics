
present(X,T):-goal(X), timestep(T).
% Observables rules
present(X,T):- visible(X, _, T).
visible(T):- visible(X, _, T).
not_occluding(X, T):-on(agent, X, T).
separator(Y, T):-on(agent, X, T), adjacent(X, Y, T), platform(X).
occludes(X,Y,T) :- present(Y, T), visible(X, _, T), not visible(Y, _, T), not separator(X, T), not not_occluding(X, T).
initiate(rotate,T):- not visible(T), timestep(T).

#modeh(1, initiate(explore(var(X),var(Y),var(Z)),var(T))).
#modeh(1, initiate(interact(var(X)),var(T))).
#maxv(4).
#modeb(1, goal(var(X))).
#modeb(1, visible(var(X), var(Z), var(T))).
#modeb(1, occludes(var(X),var(Y), var(T))).
#pos(a0@2,
{},
{initiate(rotate,0),initiate(interact(10),1),initiate(interact(10),2)},
{timestep(0).
visible(0,2,0).
goal(0).

timestep(1).
visible(0,2,1).
visible(10,10,1).
wall(10).
goal(0).

timestep(2).
visible(10,157,2).
wall(10).
goal(42).
}).

#pos(a1@1,
{},
{initiate(rotate,0),initiate(rotate,1),initiate(rotate,2),initiate(interact(10),3),initiate(interact(10),4)},
{timestep(0).
visible(0,20,0).
goal(0).

timestep(1).
visible(0,22,1).
goal(0).

timestep(2).
goal(42).

timestep(3).
visible(10,16,3).
wall(10).
goal(42).

timestep(4).
visible(10,702,4).
wall(10).
goal(42).
}).

#pos(a2@1,
{},
{initiate(interact(10),0),initiate(explore(10,42,595),1),initiate(explore(10,1,373),2),initiate(explore(1,10,2),3),initiate(rotate,4),initiate(interact(10),5)},
{timestep(0).
visible(0,0,0).
visible(10,26,0).
wall(10).
goal(0).

timestep(1).
visible(10,595,1).
wall(10).
goal(42).

adjacent(1,10, 2).
adjacent(10,1, 2).
timestep(2).
visible(1,0,2).
visible(10,373,2).
wall(10).
goal(1).

adjacent(1,10, 3).
adjacent(10,1, 3).
timestep(3).
visible(1,2,3).
visible(10,398,3).
wall(10).
goal(1).

adjacent(1,10, 4).
adjacent(10,1, 4).
timestep(4).
visible(1,2,4).
visible(10,315,4).
wall(10).
goal(1).

timestep(5).
visible(1,3,5).
visible(10,34,5).
wall(10).
goal(1).
}).

#pos(a3@4,
{initiate(interact(0),0)},
{},
{timestep(0).
visible(0,1,0).
goal(0).
}).

#pos(a4@1,
{},
{initiate(rotate,0),initiate(rotate,1),initiate(interact(10),2),initiate(rotate,3),initiate(explore(10,42,1000),4)},
{timestep(0).
visible(10,262,0).
wall(10).
goal(42).

timestep(1).
visible(10,286,1).
wall(10).
goal(42).

timestep(2).
visible(10,100,2).
wall(10).
goal(42).

timestep(3).
visible(10,595,3).
wall(10).
goal(42).

timestep(4).
visible(10,1000,4).
wall(10).
goal(42).
}).

#pos(a5@2,
{},
{initiate(explore(0,10,3),0),initiate(interact(10),1),initiate(explore(10,42,595),2)},
{timestep(0).
visible(0,3,0).
visible(10,24,0).
wall(10).
goal(0).

timestep(1).
visible(0,2,1).
visible(10,17,1).
wall(10).
goal(0).

timestep(2).
visible(10,595,2).
wall(10).
goal(42).
}).

#pos(a6@1,
{},
{initiate(rotate,0),initiate(interact(10),1),initiate(explore(10,42,643),2),initiate(interact(10),3)},
{timestep(0).
goal(42).

timestep(1).
visible(10,238,1).
wall(10).
goal(42).

timestep(2).
visible(10,643,2).
wall(10).
goal(42).

timestep(3).
visible(0,24,3).
visible(10,362,3).
wall(10).
goal(0).
}).

#pos(a7@1,
{initiate(rotate,0),initiate(explore(10,0,35),1),initiate(explore(10,0,31),2),initiate(interact(0),3)},
{},
{timestep(0).
visible(0,1,0).
goal(0).

timestep(1).
visible(0,1,1).
visible(10,35,1).
wall(10).
goal(0).

timestep(2).
visible(0,1,2).
visible(10,31,2).
wall(10).
goal(0).

timestep(3).
visible(0,2,3).
visible(10,31,3).
wall(10).
goal(0).
}).

#pos(a8@1,
{initiate(rotate,0),initiate(interact(42),1),initiate(rotate,2),initiate(interact(0),3)},
{},
{timestep(0).
goal(42).

timestep(1).
visible(10,12,1).
wall(10).
goal(42).

timestep(2).
goal(42).

timestep(3).
visible(0,1,3).
goal(0).
}).

#pos(a9@2,
{},
{initiate(interact(42),0),initiate(rotate,1),initiate(interact(42),2)},
{timestep(0).
goal(42).

timestep(1).
goal(42).

timestep(2).
visible(11,43,2).
wall(11).
goal(42).
}).

#pos(a10@1,
{},
{initiate(rotate,0),initiate(rotate,1),initiate(interact(42),2),initiate(interact(42),3)},
{timestep(0).
visible(0,1,0).
goal(0).

timestep(1).
visible(0,1,1).
goal(0).

timestep(2).
goal(42).

timestep(3).
visible(10,54,3).
wall(10).
goal(42).
}).

#pos(a11@4,
{initiate(interact(0),0)},
{},
{timestep(0).
visible(0,18,0).
goal(0).
}).

#pos(a12@3,
{},
{initiate(interact(42),0),initiate(interact(42),1)},
{timestep(0).
goal(42).

timestep(1).
goal(42).
}).

#pos(a13@3,
{},
{initiate(interact(42),0),initiate(explore(10,42,20),1)},
{timestep(0).
goal(42).

timestep(1).
visible(10,20,1).
wall(10).
goal(42).
}).

#pos(a14@3,
{},
{initiate(interact(42),0),initiate(interact(42),1)},
{timestep(0).
goal(42).

timestep(1).
visible(10,325,1).
wall(10).
goal(42).
}).

