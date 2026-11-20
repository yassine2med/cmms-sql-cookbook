-- PM compliance: share of preventive work orders closed, by month opened
SELECT substr(opened_at, 1, 7) AS month,
       COUNT(*) AS pm_scheduled,
       SUM(status = 'Closed') AS pm_closed,
       ROUND(100.0 * SUM(status = 'Closed') / COUNT(*), 1) AS compliance_pct
FROM work_orders
WHERE type = 'PM'
GROUP BY month
ORDER BY month;
