-- omop_concept_lookup.sql
-- Macro to look up OMOP concept ID from source code

{% macro omop_concept_lookup(source_code_column, source_vocabulary) %}
    (
        SELECT omop_concept_id
        FROM {{ ref('omop_concept_mappings') }}
        WHERE source_code = {{ source_code_column }}
          AND source_vocabulary = '{{ source_vocabulary }}'
        LIMIT 1
    )
{% endmacro %}

{% macro omop_concept_name_lookup(source_code_column, source_vocabulary) %}
    (
        SELECT omop_concept_name
        FROM {{ ref('omop_concept_mappings') }}
        WHERE source_code = {{ source_code_column }}
          AND source_vocabulary = '{{ source_vocabulary }}'
        LIMIT 1
    )
{% endmacro %}