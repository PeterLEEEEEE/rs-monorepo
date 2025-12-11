{{
    config(
        materialized='incremental',
        unique_key=['complex_id', 'article_id'],
        on_schema_change='fail',
        post_hook="DELETE FROM {{ this }} WHERE expire_date < CURRENT_DATE - INTERVAL '1 month'"
    )
}}

WITH source_articles AS (
    SELECT * FROM {{ source('raw', 'articles') }}
    WHERE expire_at >= CURRENT_DATE - INTERVAL '1 month'

    {% if is_incremental() %}
        AND updated_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
),

parsed AS (
    SELECT
        -- 식별자
        complex_no as complex_id,
        article_no as article_id,

        -- 기본 정보
        (payload->>'articleName')::TEXT as article_name,
        (payload->>'buildingName')::TEXT as building_name,
        (payload->>'areaName')::TEXT as area_name,

        -- 거래 정보
        (payload->>'tradeTypeCode')::TEXT as trade_type_code,
        (payload->>'tradeTypeName')::TEXT as trade_type_name,
        (payload->>'dealOrWarrantPrc')::TEXT as price_text,
        (payload->>'priceChangeState')::TEXT as price_change_state,

        -- 면적 정보
        (payload->>'area1')::NUMERIC as supply_area_sqm,
        (payload->>'area2')::NUMERIC as exclusive_area_sqm,

        -- 층/방향 정보
        (payload->>'floorInfo')::TEXT as floor_info,
        (payload->>'direction')::TEXT as direction,

        -- 위치 정보
        (payload->>'latitude')::NUMERIC as latitude,
        (payload->>'longitude')::NUMERIC as longitude,

        -- 부동산 유형
        (payload->>'realEstateTypeCode')::TEXT as real_estate_type_code,
        (payload->>'realEstateTypeName')::TEXT as real_estate_type_name,

        -- 중개사 정보
        (payload->>'realtorId')::TEXT as realtor_id,
        (payload->>'realtorName')::TEXT as realtor_name,
        (payload->>'cpName')::TEXT as cp_name,

        -- 매물 상태
        (payload->>'articleStatus')::TEXT as article_status,
        (payload->>'articleFeatureDesc')::TEXT as feature_description,

        -- 동일 주소 매물 정보
        (payload->>'sameAddrCnt')::INTEGER as same_addr_count,
        (payload->>'sameAddrMinPrc')::TEXT as same_addr_min_price,
        (payload->>'sameAddrMaxPrc')::TEXT as same_addr_max_price,

        -- 태그
        (payload->>'tagList')::JSONB as tag_list,

        -- 날짜 정보
        article_confirm_date as confirm_date,
        expire_at as expire_date,

        -- 메타데이터
        created_at,
        updated_at

    FROM source_articles
    WHERE (payload->>'articleName') IS NOT NULL
)

SELECT * FROM parsed
