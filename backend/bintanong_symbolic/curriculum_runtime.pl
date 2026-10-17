:- module(bintanong_curriculum, [run/5]).
:- use_module(library(http/json)).
:- use_module(library(time)).
:- use_module(library(lists)).

run(BundleJSON, Curriculum, Course, FactsJSON, ResultJSON) :-
    atom_json_dict(BundleJSON, Bundle, [value_string_as(atom)]),
    atom_json_dict(FactsJSON, Facts, [value_string_as(atom)]),
    ( Bundle.curriculum_id \== Curriculum -> unknown(curriculum_mismatch, absent, Result)
    ; \+ identity(Bundle, Course, _) -> unknown(unknown_course, absent, Result)
    ; identity(Bundle, Course, Record),
      ( Record.reviewed == false -> unknown(identity_unreviewed, partial, Result)
      ; evaluate(Record.rule, Course, Bundle, Facts, Result) )
    ),
    atom_json_dict(ResultJSON, Result, []).

identity(Bundle, ID, Record) :- member(Record, Bundle.courses), Record.id == ID, !.

result(State, Coverage, Satisfied, Violated, Unknown, Conflicts,
       r{outcome:State,coverage:Coverage,satisfied:Satisfied,violated:Violated,
         unknown:Unknown,conflicts:Conflicts}).

unknown(Reason, Coverage, R) :- result(unknown,Coverage,[],[],[Reason],[],R).

evaluate(Node, Owner, Bundle, Facts, R) :-
    Kind = Node.kind,
    ( Kind == unresolved -> unknown(rule_unresolved,partial,R)
    ; Kind == verified_none -> atom_concat('verified_none:',Owner,C), result(eligible,verified,[C],[],[],[],R)
    ; Kind == course -> completion(Node.course_id,Bundle,Facts,R)
    ; Kind == co_requisite -> concurrent_requirement(Node.course_id,Bundle,Facts,R)
    ; (Kind == all_of ; Kind == any_of),
      maplist(child(Owner,Bundle,Facts),Node.items,Results),
      combine(Kind,Results,R)
    ).

child(Owner,Bundle,Facts,Node,R) :- evaluate(Node,Owner,Bundle,Facts,R).

concurrent_requirement(ID,Bundle,Facts,R) :-
    ( \+ (identity(Bundle,ID,C), C.reviewed == true) ->
        atom_concat('identity_unreviewed:',ID,U), unknown(U,partial,R)
    ; completion(ID,Bundle,Facts,Completed), enrollment(ID,Facts,Enrolled),
      combine(any_of,[Completed,Enrolled],R)
    ).

enrollment(ID,Facts,R) :-
    ( memberchk(ID,Facts.enrolled), memberchk(ID,Facts.not_enrolled) ->
        atom_concat('enrollment_conflict:',ID,C), result(unknown,verified,[],[],[],[C],R)
    ; memberchk(ID,Facts.enrolled) ->
        atom_concat('enrolled:',ID,S), result(eligible,verified,[S],[],[],[],R)
    ; memberchk(ID,Facts.not_enrolled) ->
        atom_concat('not_enrolled:',ID,V), result(ineligible,verified,[],[V],[],[],R)
    ; atom_concat('enrollment_unknown:',ID,U), unknown(U,verified,R)
    ).

completion(ID,Bundle,Facts,R) :-
    ( \+ (identity(Bundle,ID,C), C.reviewed == true) ->
        atom_concat('identity_unreviewed:',ID,U), unknown(U,partial,R)
    ; memberchk(ID,Facts.passed), memberchk(ID,Facts.failed) ->
        atom_concat('completion_conflict:',ID,C), result(unknown,verified,[],[],[],[C],R)
    ; memberchk(ID,Facts.passed) ->
        atom_concat('passed:',ID,S), result(eligible,verified,[S],[],[],[],R)
    ; memberchk(ID,Facts.failed) ->
        atom_concat('not_completed:',ID,V), result(ineligible,verified,[],[V],[],[],R)
    ; atom_concat('completion_unknown:',ID,U), unknown(U,verified,R)
    ).

combine(any_of,Results,R) :- member(R,Results), R.outcome == eligible, !.
combine(Kind,Results,R) :-
    column(satisfied,Results,S), column(violated,Results,V),
    column(unknown,Results,U), column(conflicts,Results,C),
    ( member(X,Results), X.coverage == partial -> Coverage=partial ; Coverage=verified ),
    ( C \== [] -> result(unknown,Coverage,S,[],U,C,R)
    ; Kind == all_of, V \== [] -> result(ineligible,Coverage,S,V,U,[],R)
    ; U \== [] -> result(unknown,Coverage,S,[],U,[],R)
    ; V \== [] -> result(ineligible,Coverage,S,V,[],[],R)
    ; result(eligible,Coverage,S,[],[],[],R)
    ).

column(Key,Results,Values) :-
    findall(Value,(member(R,Results),get_dict(Key,R,List),member(Value,List)),Raw),
    sort(Raw,Values).
