"""
搜索链接生成模块
"""
import urllib.parse
import config


def generate_baidu_search_url(keyword: str) -> str:
    encoded_keyword = urllib.parse.quote(keyword)
    return f"{config.BAIDU_SEARCH_URL}?wd={encoded_keyword}"


def generate_enrollment_search_url(kindergarten_name: str) -> str:
    keyword = f"{kindergarten_name} 招生范围"
    return generate_baidu_search_url(keyword)


def generate_lottery_search_url(kindergarten_name: str) -> str:
    keyword = f"{kindergarten_name} 摇号结果"
    return generate_baidu_search_url(keyword)


def generate_baike_search_url(kindergarten_name: str) -> str:
    keyword = f"{kindergarten_name} 百度百科"
    return generate_baidu_search_url(keyword)


def generate_source_links(kindergarten_name: str) -> dict:
    return {
        'enrollment': generate_enrollment_search_url(kindergarten_name),
        'lottery': generate_lottery_search_url(kindergarten_name),
        'baike': generate_baike_search_url(kindergarten_name)
    }