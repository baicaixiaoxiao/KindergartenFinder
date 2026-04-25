"""
配置文件
"""

# 高德地图API配置
AMAP_API_KEY = "17cddd1db467379bbeed02492638be5c"
AMAP_BASE_URL = "https://restapi.amap.com/v3"

# 数据库配置
DB_PATH = "data/kindergarten.db"

# 搜索配置
DEFAULT_SEARCH_RADIUS = 500
SEARCH_RADIUS_OPTIONS = [500, 1000, 2000, 3000]

# POI类型配置
POI_TYPES = {
    "幼儿园": "150600",
    "医院": "090100",
    "商场": "070300",
    "学校": "150200",
}

# 百度搜索URL
BAIDU_SEARCH_URL = "https://www.baidu.com/s"

# UI配置
WINDOW_TITLE = "出行距离与幼儿园信息查询工具"
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700