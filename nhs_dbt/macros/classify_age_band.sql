-- classify_age_band.sql
-- Reusable macro for NHS standard age bands

{% macro classify_age_band(age_column) %}
    CASE
        WHEN {{ age_column }} < 18 THEN '0-17'
        WHEN {{ age_column }} BETWEEN 18 AND 29 THEN '18-29'
        WHEN {{ age_column }} BETWEEN 30 AND 39 THEN '30-39'
        WHEN {{ age_column }} BETWEEN 40 AND 49 THEN '40-49'
        WHEN {{ age_column }} BETWEEN 50 AND 59 THEN '50-59'
        WHEN {{ age_column }} BETWEEN 60 AND 69 THEN '60-69'
        WHEN {{ age_column }} BETWEEN 70 AND 79 THEN '70-79'
        WHEN {{ age_column }} BETWEEN 80 AND 89 THEN '80-89'
        ELSE '90+'
    END
{% endmacro %}