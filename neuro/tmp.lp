
%timestep(0..0).
present(X,T):-goal(X), timestep(T).
% Observables rules
present(X,T):- visible(X, _, T).
visible(T):- visible(X, _, T).
not_occluding(X, T):-on(agent, X, T).
separator(Y, T):-on(agent, X, T), adjacent(X, Y, T), platform(X).
occludes(X,Y,T) :- present(Y, T), visible(X, _, T), not visible(Y, _, T), not separator(X, T), not not_occluding(X, T).

% Observables - > actions: this is what we need to learn
%:- initiate(explore(X1,Y,_), T), initiate(explore(X2,Y,_), T), X1 != X2.
%:~initiate(explore(X,Y,Z),T).[Z@1,X,Z]
initiate(rotate,T):- not visible(T), timestep(T).#modeh(1, initiate(explore(var(X),var(Y),var(Z)),var(T))).
#modeh(1, initiate(interact(var(X)),var(T))).
#maxv(4).

        #modeb(1, goal(var(X))).
        #modeb(1, visible(var(X), var(Z), var(T))).
        #modeb(1, occludes(var(X),var(Y), var(T))).
#pos(a0@1,
{},
{initiate(rotate,0),initiate(interact(10),1),initiate(interact(10),2)},
{timestep(0).
goal(42).

timestep(1).
visible(10,181,1).
wall(10).
goal(42).

timestep(2).
visible(10,667,2).
wall(10).
goal(42).
}).

#pos(a1@1,
{},
{initiate(interact(42),0),initiate(rotate,1),initiate(explore(11,1,10),2),initiate(interact(1),3)},
{timestep(0).
goal(42).

timestep(1).
goal(42).

adjacent(1,11, 2).
adjacent(11,1, 2).
timestep(2).
visible(1,1,2).
visible(11,10,2).
wall(11).
goal(1).

adjacent(1,11, 3).
adjacent(11,1, 3).
timestep(3).
visible(1,1,3).
visible(11,10,3).
wall(11).
goal(1).
}).

#pos(a2@2,
{initiate(rotate,0),initiate(interact(0),1)},
{},
{timestep(0).
goal(42).

timestep(1).
visible(0,14,1).
goal(0).
}).

#pos(a3@1,
{},
{initiate(explore(10,0,11),0),initiate(explore(10,0,11),1),initiate(interact(10),2),initiate(interact(42),3)},
{timestep(0).
visible(0,0,0).
visible(10,11,0).
wall(10).
goal(0).

timestep(1).
visible(0,1,1).
visible(10,11,1).
wall(10).
goal(0).

timestep(2).
visible(0,0,2).
visible(10,11,2).
wall(10).
goal(0).

timestep(3).
visible(10,607,3).
wall(10).
goal(42).
}).

#pos(a4@2,
{initiate(rotate,0),initiate(explore(0,10,1),1),initiate(rotate,2),initiate(explore(0,10,1),3),initiate(interact(0),4)},
{},
{timestep(0).
goal(42).

timestep(1).
visible(0,1,1).
visible(10,9,1).
wall(10).
goal(0).

timestep(2).
visible(0,1,2).
visible(10,8,2).
wall(10).
goal(0).

timestep(3).
visible(0,1,3).
visible(10,8,3).
wall(10).
goal(0).

timestep(4).
visible(0,1,4).
visible(10,7,4).
wall(10).
goal(0).
}).

#pos(a5@1,
{initiate(interact(42),0),initiate(rotate,1),initiate(rotate,2),initiate(explore(10,42,96),3),initiate(interact(0),4)},
{},
{timestep(0).
goal(42).

timestep(1).
visible(0,2,1).
visible(10,53,1).
wall(10).
goal(0).

timestep(2).
visible(10,92,2).
wall(10).
goal(42).

timestep(3).
visible(10,96,3).
wall(10).
goal(42).

timestep(4).
visible(0,5,4).
visible(10,145,4).
wall(10).
goal(0).
}).

#pos(a6@1,
{},
{initiate(interact(42),0),initiate(interact(42),1)},
{timestep(0).
goal(42).

timestep(1).
goal(42).
}).

#pos(a7@10,
{initiate(interact(42),0),initiate(rotate,1),initiate(rotate,2),initiate(interact(1),3)},
{},
{timestep(0).
goal(42).

timestep(1).
goal(42).

timestep(2).
visible(1,57,2).
goal(1).

timestep(3).
visible(1,48,3).
goal(1).
}).

#pos(a8@2,
{},
{initiate(rotate,0),initiate(rotate,1),initiate(rotate,2),initiate(interact(10),3),initiate(interact(42),4)},
{timestep(0).
visible(0,1,0).
goal(0).

timestep(1).
visible(0,1,1).
goal(0).

timestep(2).
visible(0,1,2).
goal(0).

timestep(3).
visible(10,7,3).
wall(10).
goal(42).

timestep(4).
visible(10,429,4).
wall(10).
goal(42).
}).

#pos(a9@2,
{initiate(interact(10),0)},
{},
{adjacent(0,10, 0).
adjacent(10,0, 0).
timestep(0).
visible(0,2,0).
visible(10,24,0).
wall(10).
goal(0).
}).

#pos(a10@8,
{initiate(rotate,0),initiate(explore(10,42,192),1),initiate(interact(0),2)},
{},
{timestep(0).
goal(42).

timestep(1).
visible(10,192,1).
wall(10).
goal(42).

timestep(2).
visible(0,1,2).
visible(10,188,2).
wall(10).
goal(0).
}).

#pos(a11@1,
{},
{initiate(interact(42),0),initiate(interact(42),1)},
{timestep(0).
goal(42).

timestep(1).
goal(42).
}).

#pos(a12@1,
{},
{initiate(explore(10,42,20),0),initiate(rotate,1),initiate(rotate,2),initiate(rotate,3),initiate(explore(10,42,579),4)},
{timestep(0).
visible(10,20,0).
wall(10).
goal(42).

timestep(1).
visible(10,140,1).
wall(10).
goal(42).

timestep(2).
goal(42).

timestep(3).
visible(10,268,3).
wall(10).
goal(42).

timestep(4).
visible(10,579,4).
wall(10).
goal(42).
}).

#pos(a13@2,
{initiate(rotate,0),initiate(interact(0),1)},
{},
{timestep(0).
goal(42).

timestep(1).
visible(0,8,1).
goal(0).
}).

#pos(a14@1,
{},
{initiate(rotate,0),initiate(rotate,1),initiate(interact(42),2),initiate(rotate,3),initiate(explore(10,42,82),4)},
{timestep(0).
visible(0,3,0).
goal(0).

timestep(1).
goal(42).

timestep(2).
visible(10,111,2).
wall(10).
goal(42).

timestep(3).
goal(42).

timestep(4).
visible(10,82,4).
wall(10).
goal(42).
}).

