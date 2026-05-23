CREATE VIEW IF NOT EXISTS Num AS
    SELECT n.*, u.affectation_id
    FROM Numerotation n
    JOIN "user" u ON n.user_id = u.id;

CREATE VIEW IF NOT EXISTS Roads AS
    SELECT
        r.*,
        u.affectation_id,
        CASE
            WHEN r.decision_number IS NOT NULL AND r.decision_number != '' THEN 1
            ELSE 0
        END AS has_decision
    FROM "RefLine" r
    JOIN "user" u ON r.user_id = u.id;

CREATE VIEW IF NOT EXISTS Pan AS
    SELECT
        p.*,
        o.type || ' ' || o.nom AS org,
        c.type || ' ' || c.nom AS city,
        r.type || ' ' || r.nom AS road,
        u.affectation_id
    FROM Pannautage p
    LEFT JOIN "RefLine" r ON p.road_id = r.id
    LEFT JOIN refpolychild c ON p.subdivision_id = c.id
    LEFT JOIN reforg o ON p.organization_id = o.id
    JOIN "user" u ON p.user_id = u.id;

CREATE VIEW IF NOT EXISTS Pan2 AS
    SELECT *, COALESCE(city, org, road) AS label FROM Pan;
