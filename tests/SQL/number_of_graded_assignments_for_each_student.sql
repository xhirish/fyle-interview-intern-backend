-- Write query to get number of graded assignments for each student:
SELECT student_id, COUNT(*) AS graded_assignments_count
FROM assignments
WHERE status = 'graded'
GROUP BY student_id;
