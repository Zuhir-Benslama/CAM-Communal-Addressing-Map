create view Num as
    SELECT n.*, u.affectation_id
    FROM Numerotation n
    JOIN user u ON n.uid = u.id;



create view Roads as
    SELECT
    r.*,
    u.affectation_id,
        CASE
            WHEN r.num_decision IS NOT NULL AND r.num_decision != '' THEN 1
            ELSE 0
        END AS has_decision
    FROM RefLine r
    JOIN user u ON r.uid = u.id;



create view Pan as

SELECT
    p.*,
    o.type || ' ' || o.nom AS org,
    c.type|| ' ' || c.nom AS city,
    r.type|| ' ' || r.nom  AS road,
    u.affectation_id
FROM
    Pannautage p
LEFT JOIN RefLine r ON p.idline = r.pkuid
LEFT JOIN  refpolychild c ON p.idPoly = c.pkuid
LEFT JOIN reforg o ON p.idOrg = o.pkuid
JOIN user u ON p.uid = u.id;


 create view Pan2 as
select *, COALESCE(city,org,road ) as label from Pan;



