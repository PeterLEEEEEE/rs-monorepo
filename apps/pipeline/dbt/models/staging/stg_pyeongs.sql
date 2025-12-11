{{
    config(
        materialized='incremental',
        unique_key=['complex_id', 'pyeong_id'],
        on_schema_change='fail'
    )
}}

WITH source_complex_details AS (
    SELECT * FROM {{ source('raw', 'complex_details') }}

    {% if is_incremental() %}
        WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
),

-- JSONB 배열(pyeongs)을 테이블로 풀기
parsed AS (
    SELECT
        -- 식별자
        complex_no as complex_id,
        (pyeong_elem->>'pyeongNo')::TEXT as pyeong_id,

        -- 평형명
        (pyeong_elem->>'pyeongName')::TEXT as pyeong_name,      -- "81C", "102A"
        (pyeong_elem->>'pyeongName2')::TEXT as pyeong_name2,    -- "24C", "31A"

        -- 면적 정보
        (pyeong_elem->>'supplyArea')::NUMERIC as supply_area_sqm,
        (pyeong_elem->>'supplyAreaDouble')::NUMERIC as supply_area_double,
        (pyeong_elem->>'exclusiveArea')::NUMERIC as exclusive_area_sqm,
        (pyeong_elem->>'exclusivePyeong')::NUMERIC as exclusive_area_pyeong,

        -- 평면도 URL
        (pyeong_elem->>'grandPlanUrl')::TEXT as grand_plan_url,

        -- 메타데이터
        created_at,
        updated_at

    FROM source_complex_details,
    LATERAL jsonb_array_elements(payload->'pyeongs') AS pyeong_elem
    WHERE payload->'pyeongs' IS NOT NULL
)

SELECT * FROM parsed
