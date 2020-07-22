% STATE
present(1, 1).
present(1, 2).
% visible(399, 1).
% visible(398, 1).

%STATE LOGIC
present(X, T):- visible(X, T).
obstructs(X,Y, T) :- present(X, T), present(Y, T), visible(X, T), not visible(Y, T).

% ACTION STARTERS
%initiate(explore(X,Y), T) :- visible(X, T), obstructs(X,Y, T), not visited(X, T).
%initiate(interact(X), T):- visible(X, T), goal(X).
% init:-initiate(interact(X), T).
% init:-initiate(explore(X,Y), T).
% initiate(rotate, T):- not init.
% initiate(rotate, T):- not visible(X, T), .

% ACTION ROLLING CHECK TERMINATORS
check(visible(Y),T):- initiate(explore(X,Y),T).
check(time, T):- initiate(explore(X,Y),T).
check(time, T):- initiate(interact(X),T).

#modeb(1, visible(var(X), var(T))).
#modeb(1, obstructs(var(X),var(Y), var(T))).
#modeb(1, visited(var(X), var(T))).
#modeb(1, goal(var(X), var(T))).
#modeh(1, initiate(explore(var(X),var(Y)), var(T))).
#modeh(1, initiate(interact(var(X)), var(T))).

#pos(a@10, {initiate(explore(2,1),1), initiate(interact(1),2)}, {}, {visible(2,1). obstructs(2,1,1). visible(1,2). goal(1).}).

present(goal).
present(X):- visible(X).
obstructs(X,Y) :- present(X), present(Y), visible(X), not visible(Y).
initiate(explore(X,Y)) :- visible(X), obstructs(X,Y).
initiate(interact(goal)):- visible(goal).

check(visible(Y)):- initiate(explore(X,Y)).
check(time):- initiate(explore(X,Y)).
check(time):- initiate(interact(goal)).

% BK
goal(0).
present(0).
% visible(1).
% visible(2).
% visible(3).
% visible(4).
platform(1).
on(agent, 1).
adjacent(1, 2).

% Observables rules
present(X):- visible(X).
visible:- visible(X).
not_obstructing(X):-on(agent, X).
separator(Y):-on(agent, X), adjacent(X, Y), platform(X).
obstructs(X,Y) :- present(Y), visible(X), not visible(Y), not separator(X), not not_obstructing(X).


% Observables - > actions
initiate(explore(X,Y)) :- visible(X), obstructs(X,Y).
initiate(interact(X)):- visible(X), goal(X).
initiate(rotate):- not visible.

% Completion checks checks
check(visible(Y)):- initiate(explore(X,Y)).
check(time):- initiate(explore(X,Y)).
check(time):- initiate(interact(goal)).


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
present(X):- visible(X).
visible:- visible(X).
not_obstructing(X):-on(agent, X).
separator(Y):-on(agent, X), adjacent(X, Y), platform(X).
obstructs(X,Y) :- present(Y), visible(X), not visible(Y), not separator(X), not not_obstructing(X).

% #max{}
initiate(explore(X,Y)) :- #max{Z:initiate(possible_explore(X,Y,Z))}.
% Observables - > actions
initiate(possible_explore(X,Y,Z)) :- visible(X,Z), obstructs(X,Y).
initiate(interact(X)):- visible(X), goal(X).
initiate(rotate):- not visible.

% Completion checks checks
check(visible(Y)):- initiate(explore(X,Y)).
check(time):- initiate(explore(X,Y)).
check(time):- initiate(interact(goal)).