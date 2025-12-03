import json
import httpx

from src.core.utils import get_cookies_headers

from langchain_core.tools import tool


@tool
def get_complex_infos():
    """_summary_

    Returns:
        dict: complex overview information
    """

    with open("data/complex_data.json", "r") as f:
        data = json.load(f)
    
    new_data = []
    for item in data.get("items", []):
        new_data.append({
            "complexNo": item.get("complexNo"),
            "complexName": item.get("complexName"),
            "Address": item.get("cortarAddress"),
        })
    return f"다음 데이터는 각 건물 별 이름과 id값 그리고 건물이 위치한 주소입니다. {new_data}"

@tool
def get_complex_id(query: str):
    """

    Args:
        query (str): Search query for apt ID
    """

    
    return f"{query}의 complex_id 값은 236입니다."


@tool
def get_complex_overview(complex_id: str):
    """_summary_

    Args:
        complex_id (str): complex_id for the apartment complex

    Returns:
        dict: complex information about lease and sale prices
    """

    cookies, headers = get_cookies_headers()
    url = f"https://new.land.naver.com/api/complexes/overview/{complex_id}?complexNo={complex_id}"
    response = httpx.get(url, cookies=cookies, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    
    res_dict = {
        "아파트 명": data["complexName"],
        "세대 수": data["totalHouseHoldCount"],
        "매매 최고 가격": data["maxPriceByLetter"],
        "매매 최저 가격": data["minPriceByLetter"],
        "전세 최고 가격": data["maxLeasePriceByLetter"],
        "전세 최저 가격": data["minLeasePriceByLetter"],
    }
    
    return res_dict

@tool
def search_apartment_by_name(query: str):
    """_summary_
    Search for an apartment by its name.
    
    Args:
        query (str): user query
    """