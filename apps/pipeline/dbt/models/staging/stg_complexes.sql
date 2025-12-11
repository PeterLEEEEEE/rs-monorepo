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

parsed AS (
    SELECT
        -- 식별자
        complex_no as complex_id,

        -- 기본 정보
        (payload->>'complexName')::TEXT as complex_name,
        (payload->>'complexType')::TEXT as complex_type,
        (payload->>'complexTypeName')::TEXT as complex_type_name,

        -- 규모 정보
        (payload->>'totalDongCount')::INTEGER as total_dong_count,
        (payload->>'totalHouseHoldCount')::INTEGER as total_household_count,

        -- 사용 승인일
        (payload->>'useApproveYmd')::TEXT as use_approve_ymd,

        -- 위치 정보
        (payload->>'latitude')::NUMERIC as latitude,
        (payload->>'longitude')::NUMERIC as longitude,

        -- 면적 정보
        (payload->>'minArea')::NUMERIC as min_area,
        (payload->>'maxArea')::NUMERIC as max_area,

        -- 매매가 정보
        (payload->>'minPrice')::BIGINT as min_price,
        (payload->>'maxPrice')::BIGINT as max_price,
        (payload->>'minPriceByLetter')::TEXT as min_price_text,
        (payload->>'maxPriceByLetter')::TEXT as max_price_text,

        -- 전세가 정보
        (payload->>'minLeasePrice')::BIGINT as min_lease_price,
        (payload->>'maxLeasePrice')::BIGINT as max_lease_price,
        (payload->>'minLeasePriceByLetter')::TEXT as min_lease_price_text,
        (payload->>'maxLeasePriceByLetter')::TEXT as max_lease_price_text,

        -- 메타데이터
        created_at,
        updated_at

    FROM source_complex_details
    WHERE payload->>'complexName' IS NOT NULL
)

SELECT * FROM parsed
