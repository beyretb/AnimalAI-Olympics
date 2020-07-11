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
