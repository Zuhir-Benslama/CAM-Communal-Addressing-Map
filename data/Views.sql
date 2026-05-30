CREATE VIEW IF NOT EXISTS Num AS
    SELECT n.*, u.affectation_id
    FROM numbering n
    JOIN "user" u ON n.user_id = u.id;

CREATE VIEW IF NOT EXISTS Roads AS
    SELECT
        r.*,
        u.affectation_id,
        CASE
            WHEN r.decision_number IS NOT NULL AND r.decision_number != '' THEN 1
            ELSE 0
        END AS has_decision
    FROM "road" r
    JOIN "user" u ON r.user_id = u.id;

CREATE VIEW IF NOT EXISTS Pan AS
    SELECT
        p.*,
        o.type || ' ' || o.name AS org,
        c.type || ' ' || c.name AS city,
        r.type || ' ' || r.name AS road,
        u.affectation_id
    FROM panel_sign p
    LEFT JOIN "road" r ON p.road_id = r.id
    LEFT JOIN subdivision c ON p.subdivision_id = c.id
    LEFT JOIN organization o ON p.organization_id = o.id
    JOIN "user" u ON p.user_id = u.id;

CREATE VIEW IF NOT EXISTS Pan2 AS
    SELECT *, COALESCE(city, org, road) AS label FROM Pan;
