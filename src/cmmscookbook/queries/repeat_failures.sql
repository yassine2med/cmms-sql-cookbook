-- Repeat failures: assets with three or more corrective work orders
SELECT a.asset_id,
       a.name,
       COUNT(*) AS corrective_wo,
       MIN(substr(w.opened_at, 1, 10)) AS first_seen,
       MAX(substr(w.opened_at, 1, 10)) AS last_seen
FROM work_orders w
JOIN assets a ON a.asset_id = w.asset_id
WHERE w.type = 'CM'
GROUP BY a.asset_id, a.name
HAVING COUNT(*) >= 3
ORDER BY corrective_wo DESC, a.asset_id;
