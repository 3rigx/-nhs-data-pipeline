-- cohort_builder.sql
-- Reusable macro for standardised cohort output format
-- Ensures all cohorts have consistent metadata columns

{% macro cohort_header(cohort_name, cohort_version, cohort_description) %}
    -- Cohort metadata
    '{{ cohort_name }}' AS cohort_name,
    '{{ cohort_version }}' AS cohort_version,
    '{{ cohort_description }}' AS cohort_description,
    CURRENT_DATE AS cohort_generated_date,
    CURRENT_TIMESTAMP AS cohort_generated_at
{% endmacro %}