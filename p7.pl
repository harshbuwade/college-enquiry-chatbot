%	Facts

male(gendlal). 
male(shivshankar). 
male(harsh).

female(ganga). 
female(shivkali). 
female(sunita).

parent(gendlal, shivshankar). 
parent(gendlal, shivkali). 
parent(ganga, shivshankar). 
parent(ganga, shivkali). 
parent(shivshankar, harsh). 
parent(sunita, harsh).

%	Rules

father(X, Y) :-
parent(X, Y),
male(X).

mother(X, Y) :-
parent(X, Y), female(X).
sibling(X, Y) :-
parent(Z, X),
parent(Z, Y),
X \= Y.
grandparent(X, Y) :- parent(X, Z),
parent(Z, Y).

ancestor(X, Y) :-
parent(X, Y).
ancestor(X, Y) :-
 
parent(X, Z), ancestor(Z, Y).
