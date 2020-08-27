present(X,T):- visible(X, _, T).
        visible(T):- visible(X, _, T).
        not_occluding(X, T):-on(agent, X, T).
        separator(Y, T):-on(agent, X, T), adjacent(X, Y, T), platform(X).
        occludes(X,Y,T) :- present(Y, T), visible(X, _, T), not visible(Y, _, T), not separator(X, T), not not_occluding(X, T).
:- initiate(explore(X1,Y,_), T), initiate(explore(X2,Y,_), T), X1 != X2.
:~initiate(explore(X,Y,Z),T).[-Z@1,X,Z]
0{initiate(explore(X,Y,Z),T)}1:- visible(X,Z,T), occludes(X,Y,T).
initiate(interact(X),T):- visible(X, _,T), goal(X).
initiate(rotate,T):- not visible(T), timestep(T).

        check(visible(Y),T):- initiate(explore(X,Y,Z),T).
        check(time, 150):- initiate(explore(X,Y,Z),T).
        check(time, 150):- initiate(interact(X),T).
        check(time, 50):- initiate(rotate,T).timestep(0).
visible(10,1,0).
visible(11,22,0).

wall(10).
goal(42).
present(X,T):-goal(X), timestep(T).
