-- Technician workload: closed work orders and labor hours per technician
SELECT t.name,
       t.trade,
       COUNT(w.wo_id) AS closed_wo,
       ROUND(SUM(w.labor_hours), 1) AS labor_hours,
       ROUND(AVG(w.labor_hours), 1) AS avg_hours_per_wo
FROM technicians t
LEFT JOIN work_orders w ON w.tech_id = t.tech_id AND w.status = 'Closed'
GROUP BY t.tech_id, t.name, t.trade
ORDER BY closed_wo DESC, t.name;
