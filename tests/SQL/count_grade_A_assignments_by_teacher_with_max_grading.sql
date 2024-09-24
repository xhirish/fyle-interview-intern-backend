WITH TeacherGradingCount AS (
    -- Step 1: Count the number of assignments graded by each teacher
    SELECT teacher_id, COUNT(*) AS total_graded
    FROM assignments
    WHERE status = 'GRADED'
    GROUP BY teacher_id
),
MaxGradingTeacher AS (
    -- Step 2: Find the teacher who has graded the most assignments
    -- Use a tie-breaking approach to ensure only one teacher is selected in case of a tie
    SELECT teacher_id
    FROM TeacherGradingCount
    ORDER BY total_graded DESC, teacher_id -- Adding teacher_id to resolve ties
    LIMIT 1
)
-- Step 3: Count the number of 'Grade A' assignments given by that teacher
SELECT COUNT(*) AS grade_A_count
FROM assignments
WHERE teacher_id = (SELECT teacher_id FROM MaxGradingTeacher)
AND grade = 'A';
