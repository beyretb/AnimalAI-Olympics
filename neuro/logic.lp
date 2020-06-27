% STATE
present(398).
goal(398).
% visible(399).
% visible(398).

%STATE LOGIC
present(X):- visible(X).
obstructs(X,Y) :- present(X), present(Y), visible(X), not visible(Y).

% ACTION STARTERS
%initiate(explore(X,Y)) :- visible(X), obstructs(X,Y), not visited(X).
%initiate(interact(X)):- visible(X), goal(X).
%init:-initiate(interact(X)).
%init:-initiate(explore(X,Y)).
%initiate(rotate):- not init.

% ACTION ROLLING CHECK TERMINATORS
check(visible(Y)):- initiate(explore(X,Y)).
check(time):- initiate(explore(X,Y)).
check(time):- initiate(interact(X)).

#constant(number, 1).
#constant(number, 2).

#modeb(1,visible(var(X))).
#modeb(1, obstructs(var(X),var(Y))).
#modeb(1, visited(var(X))).
#modeb(1, goal(var(X))).
#modeh(1, initiate(explore(var(X),var(Y)))).
#modeh(1, initiate(interact(var(X)))).

#pos({initiate(explore(1,2)), visible(1), obstructs(1,2)}, {visited(1)}).
#pos({interact(1)},{visible(1), goal(1)}).
