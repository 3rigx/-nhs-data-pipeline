-- classify_los.sql
-- Reusable macro for length of stay categories

{% macro classify_los(los_column) %}
    CASE
        WHEN {{ los_column }} = 0 THEN 'Day Case'
        WHEN {{ los_column }} BETWEEN 1 AND 2 THEN 'Short Stay'
        WHEN {{ los_column }} BETWEEN 3 AND 7 THEN 'Medium Stay'
        WHEN {{ los_column }} BETWEEN 8 AND 28 THEN 'Long Stay'
        ELSE 'Very Long Stay'
    END
{% endmacro %}