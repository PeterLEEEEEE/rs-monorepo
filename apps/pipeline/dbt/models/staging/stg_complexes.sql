{{
    config(
        materialized='incremental',
        unique_key='complex_id',
        on_schema_change='fail'
    )
}}

WITH source_complex_details AS (
    SELECT * FROM {{ source('raw', 'complex_details') }}

    {% if is_incremental() %}
        WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
),

source_complexes AS (
    SELECT * FROM {{ source('raw', 'complexes') }}
),

parsed AS (
    SELECT
        -- 식별자
        cd.complex_no as complex_id,

        -- 기본 정보
        (cd.payload->>'complexName')::TEXT as complex_name,
        (cd.payload->>'complexType')::TEXT as complex_type,
        (cd.payload->>'complexTypeName')::TEXT as complex_type_name,

        -- 규모 정보
        (cd.payload->>'totalDongCount')::INTEGER as total_dong_count,
        (cd.payload->>'totalHouseHoldCount')::INTEGER as total_household_count,

        -- 사용 승인일
        (cd.payload->>'useApproveYmd')::TEXT as use_approve_ymd,

        -- 위치 정보
        (c.payload->>'cortarNo')::TEXT as address_id,
        (c.payload->>'cortarAddress')::TEXT as address,
        (cd.payload->>'latitude')::NUMERIC as latitude,
        (cd.payload->>'longitude')::NUMERIC as longitude,

        -- 면적 정보
        (cd.payload->>'minArea')::NUMERIC as min_area,
        (cd.payload->>'maxArea')::NUMERIC as max_area,

        -- 매매가 정보
        (cd.payload->>'minPrice')::BIGINT as min_price,
        (cd.payload->>'maxPrice')::BIGINT as max_price,
        (cd.payload->>'minPriceByLetter')::TEXT as min_price_text,
        (cd.payload->>'maxPriceByLetter')::TEXT as max_price_text,

        -- 전세가 정보
        (cd.payload->>'minLeasePrice')::BIGINT as min_lease_price,
        (cd.payload->>'maxLeasePrice')::BIGINT as max_lease_price,
        (cd.payload->>'minLeasePriceByLetter')::TEXT as min_lease_price_text,
        (cd.payload->>'maxLeasePriceByLetter')::TEXT as max_lease_price_text,

        -- 메타데이터
        cd.created_at,
        cd.updated_at

    FROM source_complex_details cd
    LEFT JOIN source_complexes c ON cd.complex_no = c.complex_no
    WHERE cd.payload->>'complexName' IS NOT NULL
)

SELECT * FROM parsed
