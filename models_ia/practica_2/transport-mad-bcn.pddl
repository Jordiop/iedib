(define (problem transport-mad-bcn)
    (:domain transport)
    (:objects a1 a2 bcn c1 c2 mad)
    (:init (aeroport bcn) (aeroport mad) (at a1 mad) (at a2 bcn) (at c1 mad) (at c2 bcn) (avio a1) (avio a2) (carrega c1) (carrega c2))
    (:goal (and (at c1 bcn) (at c2 mad)))
)