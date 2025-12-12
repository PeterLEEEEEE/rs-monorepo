{{
    config(
        materialized='table'
    )
}}

WITH distinct_regions AS (
    SELECT DISTINCT
        LEFT(address_id, 5) || '00000' as gu_cortar_no,
        TRIM(SUBSTRING(address FROM POSITION('시 ' IN address) + 2 FOR
            POSITION('구' IN address) - POSITION('시 ' IN address))) as gu_name
    FROM {{ ref('stg_complexes') }}
    WHERE address LIKE '%구%'
      AND address_id IS NOT NULL
),

region_codes AS (
    SELECT
        gu_cortar_no,
        gu_name,
        CASE gu_name
            WHEN '강남구' THEN 'gangnam'
            WHEN '서초구' THEN 'seocho'
            WHEN '송파구' THEN 'songpa'
            WHEN '용산구' THEN 'yongsan'
            WHEN '성동구' THEN 'seongdong'
            WHEN '마포구' THEN 'mapo'
            WHEN '동작구' THEN 'dongjak'
            WHEN '영등포구' THEN 'yeongdeungpo'
            WHEN '광진구' THEN 'gwangjin'
            WHEN '강동구' THEN 'gangdong'
            WHEN '노원구' THEN 'nowon'
            WHEN '강서구' THEN 'gangseo'
            WHEN '강북구' THEN 'gangbuk'
            WHEN '성북구' THEN 'seongbuk'
            WHEN '종로구' THEN 'jongno'
            WHEN '중구' THEN 'jung'
            WHEN '중랑구' THEN 'jungnang'
            WHEN '도봉구' THEN 'dobong'
            WHEN '양천구' THEN 'yangcheon'
            WHEN '은평구' THEN 'eunpyeong'
            WHEN '서대문구' THEN 'seodaemun'
            WHEN '관악구' THEN 'gwanak'
            WHEN '금천구' THEN 'geumcheon'
            WHEN '동대문구' THEN 'dongdaemun'
            WHEN '구로구' THEN 'guro'
            ELSE LOWER(REPLACE(gu_name, '구', ''))
        END as region_code
    FROM distinct_regions
)

SELECT
    gu_cortar_no as region_id,
    region_code,
    gu_name as region_name,
    '서울시' as city_name
FROM region_codes
ORDER BY gu_name
