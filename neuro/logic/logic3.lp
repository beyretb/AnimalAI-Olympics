% BK
goal(0).
present(0).
% Observables
visible(1,1).
visible(2,2).
visible(3,3).
visible(4,4).
platform(1).
on(agent, 1).
adjacent(1, 2).

% Observables rules
present(X):- visible(X, _).
visible:- visible(X, _).
not_obstructing(X):-on(agent, X).
separator(Y):-on(agent, X), adjacent(X, Y), platform(X).
obstructs(X,Y) :- present(Y), visible(X, _), not visible(Y, _), not separator(X), not not_obstructing(X).

% Observables - > actions
:- initiate(explore(X1,Y,_)), initiate(explore(X2,Y,_)), X1 != X2.
0{initiate(explore(X,Y,Z))}1:- visible(X,Z), obstructs(X,Y).
:~initiate(explore(X,Y,Z)).[-Z@1,X,Z]
initiate(interact(X)):- visible(X, _), goal(X).
initiate(rotate):- not visible.

% Completion checks checks
check(visible(Y)):- initiate(explore(X,Y,Z)).
check(time):- initiate(explore(X,Y,Z)).
check(time):- initiate(interact(goal)).

% All the observables
#modeb(1, visible(var(X), var(O), var(T))).
#modeb(1, obstructs(var(X),var(Y), var(T))).
#modeb(1, visited(var(X), var(T))).
#modeb(1, goal(var(X), var(T))).
% All the possible macro actions
#modeh(1, initiate(explore(var(X),var(Y)), var(T))).
#modeh(1, initiate(interact(var(X)), var(T))).


#pos(a@10, {initiate(explore(2,1),1), initiate(interact(1),2)}, {}, {visible(2,1). obstructs(2,1,1). visible(1,2). goal(1).}).