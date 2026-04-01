-- calculate_age.sql
-- Reusable macro for calculating age at a point in time

{% macro calculate_age(date_of_birth, reference_date) %}
    DATE_DIFF('year', {{ date_of_birth }}, {{ reference_date }})
{% endmacro %}