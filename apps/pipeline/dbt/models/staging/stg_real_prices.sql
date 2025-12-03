{{
    config(
        materialized='incremental',
        unique_key=['complex_id', 'pyeong_id', 'floor', 'deal_price', 'trade_date'],
        on_schema_change='fail'
    )
}}

WITH source_real_prices AS (
    SELECT * FROM {{ source('raw', 'real_prices') }}

    {% if is_incremental() %}
        -- 증분: 마지막 dbt run 이후 생성된 데이터만
        WHERE created_at > (SELECT MAX(loaded_at) FROM {{ this }})
    {% endif %}
),

source_complex_details AS (
    SELECT * FROM {{ source('raw', 'complex_details') }}
),

-- JSONB 배열(pyeongs)을 테이블로 풀기
pyeong_info AS (
    SELECT
        complex_no,
        (pyeong_elem->>'pyeongNo')::TEXT as pyeong_no,
        (pyeong_elem->>'pyeongName')::TEXT as pyeong_name,        -- "86A", "91A"
        (pyeong_elem->>'pyeongName2')::TEXT as pyeong_name2,      -- "26A", "27A"
        (pyeong_elem->>'exclusiveArea')::NUMERIC as exclusive_area_sqm,
        (pyeong_elem->>'exclusivePyeong')::NUMERIC as exclusive_area_pyeong
    FROM source_complex_details,
    LATERAL jsonb_array_elements(payload->'pyeongs') AS pyeong_elem
),

parsed_real_prices AS (
    SELECT
        -- 식별자 (컬럼명 변경)
        rp.complex_no as complex_id,
        rp.area_no as pyeong_id,

        -- 거래 정보
        (rp.payload->>'dealPrice')::BIGINT as deal_price,
        (rp.payload->>'floor')::INTEGER as floor,
        rp.trade_date,
        (rp.payload->>'tradeType')::TEXT as trade_type,

        -- 메타데이터
        rp.created_at as loaded_at,
        rp.updated_at

    FROM source_real_prices rp

    -- 데이터 품질 필터
    WHERE
        (rp.payload->>'dealPrice') IS NOT NULL
        AND (rp.payload->>'dealPrice')::BIGINT > 0
        AND (rp.payload->>'floor')::INTEGER BETWEEN 1 AND 100
),

-- 평형 정보 JOIN
final AS (
    SELECT
        -- 식별자
        prp.complex_id,
        prp.pyeong_id,
        prp.floor,
        prp.trade_date,

        -- 거래 정보
        prp.deal_price,
        prp.trade_type,

        -- 평형명 (컬럼명 변경)
        pi.pyeong_name as area_m,      -- "86A", "91A", "97A"
        pi.pyeong_name2 as area_p,     -- "26A", "27A", "29A"

        -- 면적 정보
        pi.exclusive_area_sqm,
        pi.exclusive_area_pyeong,

        -- 메타데이터
        prp.loaded_at,
        prp.updated_at

    FROM parsed_real_prices prp
    LEFT JOIN pyeong_info pi
        ON prp.complex_id = pi.complex_no
        AND prp.pyeong_id = pi.pyeong_no
)

SELECT * FROM final