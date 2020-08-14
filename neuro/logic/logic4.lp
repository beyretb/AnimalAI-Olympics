% BK
timestep(1..5).
present(X,T):-goal(X), timestep(T).

% ======= Macro action grounder
present(X,T):- visible(X, _, T).
object(X):-present(X,T).
occlusion(O):-visible(_,O,_).
explore(X,Y,O):-object(X), object(Y), occlusion(O).
interact(X):-object(X).
rotate.
% =======
% Observables rules
present(X,T):- visible(X, _, T).
visible(T):- visible(X, _, T).
not_occluding(X, T):-on(agent, X, T).
separator(Y, T):-on(agent, X, T), adjacent(X, Y, T), platform(X).
occludes(X,Y,T) :- present(Y, T), visible(X, _, T), not visible(Y, _, T), not separator(X, T), not not_occluding(X, T).

% Observables - > actions: this is what we need to learn
:- initiate(explore(X1,Y,_), T), initiate(explore(X2,Y,_), T), X1 != X2.
:~initiate(explore(X,Y,Z),T).[Z@1,X,Z]

0{initiate(explore(X,Y,Z),T)}1:- visible(X,Z,T), occludes(X,Y,T).
initiate(interact(X),T):- visible(X, _,T), goal(X).
initiate(rotate,T):- not visible(T), timestep(T).

% Completion checks checks
check(visible(Y),T):- initiate(explore(X,Y,Z),T).
check(time, T):- initiate(explore(X,Y,Z),T).
check(time, T):- initiate(interact(X),T).
check(time, T):- initiate(rotate,T).

% All the observables
#modeb(1, goal(var(X))).
#modeb(1, visible(var(X), var(Z), var(T))).
#modeb(1, visible(var(T))).
#modeb(1, occludes(var(X),var(Y), var(T))).
#modeb(1, timestep(var(T))).
% #modeb(2, initiate(explore(var(X),var(Y), var(Z)), var(T))).

% All the possible macro actions
#modeh(1, initiate(explore(var(X),var(Y), var(Z)), var(T))).
#modeh(1, initiate(interact(var(X)), var(T))).
#modeh(1, initiate(rotate, var(T))).
#maxv(4).
% Weak constraints
% #modeo(1,initiate(explore(var(X), var(Y), var(Z)),var(T))).
% #maxp(1).
% #weight(1).

#pos(a1@5, {
	initiate(explore(4,0,4),1),
	initiate(interact(0),2)}, {}, {
	visible(1,1,1).
	visible(2,2,1).
	visible(3,3,1).
	visible(4,4,1).
	platform(1).
	on(agent, 1,1).
	adjacent(1, 2, 1).
	goal(0).
	visible(0,1,2).}).

#pos({
	initiate(rotate,1),
	initiate(interact(0),2)}, {}, {
	goal(0).
	visible(0,1,2).
	}).

#neg({
	initiate(rotate,1),
	initiate(interact(1),2)}, {}, {
	goal(0).
	visible(0,1,2).
	visible(1,1,2).
		}).

% #neg({
% 	initiate(rotate,1),
% 	initiate(interact(1),2)}, {}, {
% 	goal(0).
% 	visible(0,1,2).
% 	visible(0,1,1).
% 		}).

