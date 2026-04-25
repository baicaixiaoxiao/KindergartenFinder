"""
搜索服务模块
"""
from typing import List, Dict, Optional
from core.api.gaode import GaodeAPI, calculate_distance
from core.api.search import generate_source_links
from core.database.db_manager import DatabaseManager
import config


class SearchService:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.gaode_api = GaodeAPI()

    def search_nearby(self, address: str, keyword: str, radius: int = 1000, 
                      poi_type: str = None) -> List[Dict]:
        geocode_result = self.gaode_api.geocode(address)
        if not geocode_result:
            return []

        origin_lng = geocode_result['lng']
        origin_lat = geocode_result['lat']
        origin_location = f"{origin_lng},{origin_lat}"

        poi_type_code = config.POI_TYPES.get(poi_type) if poi_type else None
        
        pois = self.gaode_api.poi_search(
            keywords=keyword,
            city=geocode_result.get('city', '成都'),
            types=poi_type_code,
            location=origin_location,
            radius=radius,
            page=1,
            offset=20
        )

        results = []
        for poi in pois:
            if poi['lng'] is None or poi['lat'] is None:
                continue

            distance = calculate_distance(origin_lat, origin_lng, poi['lat'], poi['lng'])
            poi_location = f"{poi['lng']},{poi['lat']}"

            walking_result = self.gaode_api.walking_route(origin_location, poi_location)
            transit_result = self.gaode_api.transit_route(origin_location, poi_location)

            kg_data = self.db_manager.get_kindergarten_by_name(poi['name'])
            lottery_data = None
            if kg_data:
                lottery_data = self.db_manager.get_latest_lottery(kg_data['id'])

            source_links = generate_source_links(poi['name'])

            result = {
                'name': poi['name'],
                'address': poi.get('address', ''),
                'type': poi.get('type', ''),
                'distance': distance,
                'lng': poi['lng'],
                'lat': poi['lat'],
                'walking': self._format_walking(walking_result),
                'transit': self._format_transit(transit_result),
                'kindergarten': kg_data,
                'lottery': lottery_data,
                'source_links': source_links
            }
            results.append(result)

        results.sort(key=lambda x: x['distance'])
        return results

    def _format_walking(self, walking_result: Optional[Dict]) -> Optional[Dict]:
        if not walking_result:
            return None
        return {
            'duration': walking_result.get('duration', 0),
            'distance': walking_result.get('distance', 0),
            'duration_text': self._format_duration(walking_result.get('duration', 0)),
            'distance_text': self._format_distance(walking_result.get('distance', 0))
        }

    def _format_transit(self, transit_result: Optional[Dict]) -> Optional[Dict]:
        if not transit_result:
            return None

        segments = transit_result.get('segments', [])
        if not segments:
            return None

        first_segment = segments[0]
        line_info = first_segment.get('line', {})
        
        departure_stop = first_segment.get('departure_stop')
        arrival_stop = first_segment.get('arrival_stop')
        station_count = first_segment.get('station_count')

        return {
            'duration': transit_result.get('duration', 0),
            'distance': transit_result.get('distance', 0),
            'duration_text': self._format_duration(transit_result.get('duration', 0)),
            'distance_text': self._format_distance(transit_result.get('distance', 0)),
            'line_name': first_segment.get('line_name'),
            'departure_stop': departure_stop,
            'arrival_stop': arrival_stop,
            'station_count': station_count,
            'segments': segments
        }

    def _format_duration(self, seconds: int) -> str:
        if seconds < 60:
            return f"{seconds}秒"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}分钟"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}小时{minutes}分钟"

    def _format_distance(self, meters: int) -> str:
        if meters < 1000:
            return f"{meters}米"
        else:
            km = meters / 1000
            return f"{km:.1f}公里"

    def save_search_history(self, address_id: int, keyword: str):
        self.db_manager.add_search_history(address_id, keyword)