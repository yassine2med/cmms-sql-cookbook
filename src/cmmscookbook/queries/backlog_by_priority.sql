-- Open backlog: work orders not yet closed, by priority and status
SELECT priority,
       SUM(status = 'Open')        AS open_wo,
       SUM(status = 'In Progress') AS in_progress,
       COUNT(*)                    AS total
FROM work_orders
WHERE status <> 'Closed'
GROUP BY priority
ORDER BY priority;
