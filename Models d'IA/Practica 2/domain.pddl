(define (domain transport)
    (:predicates
        (A ?c ?r)
        (Dins ?c ?a)
        (Carrega ?c)
        (Avio ?a)
        (Aeroport ?r))
        
    (:action Carregar
        :parameters (?c ?a ?r)
        :precondition (and (A ?c ?r) (A ?a ?r) (Carrega ?c) (Avio ?a) (Aeroport ?r) )
        :effect(and (not(A ?c ?r)) (Dins ?c ?a)  ) )
        
        
    (:action Descarregar
        :parameters (?c ?a ?r)
        :precondition (and (Dins ?c ?a) (A ?a ?r) (Carrega ?c) (Avio ?a) (Aeroport ?r) )
        :effect(and (A ?c ?r) (not (dins ?c ?a))))
        
    (:action Volar
        :parameters (?a ?origen ?desti)
        :precondition (and (A ?a ?origen) (Avio ?a) (Aeroport ?origen) (Aeroport ?desti))
        :effect (and (not(A ?a ?origen)) (A ?a ?desti))))  