"""
高德地图API封装
"""
import requests
import urllib.parse
from typing import Dict, List, Optional
import config


class GaodeAPI:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.AMAP_API_KEY
        self.base_url = config.AMAP_BASE_URL

    def _request(self, endpoint: str, params: Dict) -> Dict:
        params['key'] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {'status': '0', 'info': str(e)}

    def geocode(self, address: str, city: str = "成都") -> Optional[Dict]:
        params = {
            'address': address,
            'city': city,
            'output': 'json'
        }
        result = self._request('geocode/geo', params)
        if result.get('status') == '1' and result.get('geocodes'):
            geocode = result['geocodes'][0]
            return {
                'province': geocode.get('province'),
                'city': geocode.get('city'),
                'district': geocode.get('district'),
                'location': geocode.get('location'),
                'lng': float(geocode['location'].split(',')[0]),
                'lat': float(geocode['location'].split(',')[1])
            }
        return None

    def poi_search(self, keywords: str, city: str = "成都", types: str = None, 
                   location: str = None, radius: int = 1000, page: int = 1, 
                   offset: int = 20) -> List[Dict]:
        params = {
            'keywords': keywords,
            'city': city,
            'citylimit': 'true',
            'offset': offset,
            'page': page,
            'extensions': 'all'
        }
        if types:
            params['types'] = types
        if location:
            params['location'] = location
        if radius:
            params['radius'] = radius

        result = self._request('place/text', params)
        pois = []
        if result.get('status') == '1' and result.get('pois'):
            for poi in result['pois']:
                location = poi.get('location', '').split(',')
                pois.append({
                    'id': poi.get('id'),
                    'name': poi.get('name'),
                    'type': poi.get('type'),
                    'typecode': poi.get('typecode'),
                    'address': poi.get('address'),
                    'location': poi.get('location'),
                    'lng': float(location[0]) if location and len(location) == 2 else None,
                    'lat': float(location[1]) if location and len(location) == 2 else None,
                    'distance': poi.get('distance'),
                    'pname': poi.get('pname'),
                    'cityname': poi.get('cityname'),
                    'adname': poi.get('adname')
                })
        return pois

    def walking_route(self, origin: str, destination: str) -> Optional[Dict]:
        params = {
            'origin': origin,
            'destination': destination,
            'strategy': '0'
        }
        result = self._request('direction/walking', params)
        if result.get('status') == '1' and result.get('route'):
            route = result['route']
            if route.get('paths') and len(route['paths']) > 0:
                path = route['paths'][0]
                return {
                    'distance': int(path.get('distance', 0)),
                    'duration': int(path.get('duration', 0)),
                    'steps': self._parse_steps(path.get('steps', []))
                }
        return None

    def transit_route(self, origin: str, destination: str, city: str = "成都") -> Optional[Dict]:
        params = {
            'origin': origin,
            'destination': destination,
            'city': city,
            'strategy': '0'
        }
        result = self._request('direction/transit/integrated', params)
        if result.get('status') == '1' and result.get('route'):
            route = result['route']
            if route.get('transits') and len(route['transits']) > 0:
                transit = route['transits'][0]
                return {
                    'distance': int(transit.get('distance', 0)),
                    'duration': int(transit.get('duration', 0)),
                    'segments': self._parse_transit_segments(transit.get('segments', []))
                }
        return None

    def _parse_steps(self, steps: List[Dict]) -> List[Dict]:
        parsed_steps = []
        for step in steps:
            parsed_steps.append({
                'instruction': step.get('instruction'),
                'distance': int(step.get('distance', 0)),
                'duration': int(step.get('duration', 0)),
                'road': step.get('road'),
                'orientation': step.get('orientation')
            })
        return parsed_steps

    def _parse_transit_segments(self, segments: List[Dict]) -> List[Dict]:
        parsed_segments = []
        for segment in segments:
            seg_info = {
                'entry': segment.get('entry', {}),
                'exit': segment.get('exit', {}),
                'line': segment.get('line', {}),
                'walking': segment.get('walking', {})
            }
            
            line_info = segment.get('line', {})
            if line_info:
                seg_info['line_name'] = line_info.get('name')
                seg_info['line_type'] = line_info.get('type')
                departure_stop = line_info.get('departure_stop', {})
                arrival_stop = line_info.get('arrival_stop', {})
                seg_info['departure_stop'] = departure_stop.get('name') if departure_stop else None
                seg_info['arrival_stop'] = arrival_stop.get('name') if arrival_stop else None
                seg_info['station_count'] = line_info.get('station_count')
            
            parsed_segments.append(seg_info)
        return parsed_segments


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    import math
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c