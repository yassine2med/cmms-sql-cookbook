-- MTTR: mean hours from start of work to close, closed corrective work by asset category
SELECT a.category,
       COUNT(*) AS repairs,
       ROUND(AVG((julianday(w.closed_at) - julianday(w.started_at)) * 24), 1) AS mttr_hours
FROM work_orders w
JOIN assets a ON a.asset_id = w.asset_id
WHERE w.type = 'CM' AND w.status = 'Closed'
GROUP BY a.category
ORDER BY mttr_hours DESC;
