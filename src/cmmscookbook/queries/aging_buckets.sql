-- Aging: how long the unclosed work orders have been waiting, as of :asof
SELECT CASE
         WHEN age_days <= 7  THEN '1: 0-7 days'
         WHEN age_days <= 30 THEN '2: 8-30 days'
         WHEN age_days <= 90 THEN '3: 31-90 days'
         ELSE '4: over 90 days'
       END AS bucket,
       COUNT(*) AS work_orders,
       ROUND(AVG(age_days), 1) AS avg_age_days
FROM (
    SELECT julianday(:asof) - julianday(opened_at) AS age_days
    FROM work_orders
    WHERE status <> 'Closed'
)
GROUP BY bucket
ORDER BY bucket;
