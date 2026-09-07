import re
import requests
from urllib.parse import urljoin

def process(hostName, fullPath):
    # mediainfo": {
    #    "tracks": [
    #        {
    #            "track_type": "General",
    #            "internet_media_type"
    #            "duration" 
    #        },
    #            "track_type": "Video",
    #            "width",
    #            "height"    

    url = f"{hostName}/{fullPath}"
    response = requests.get(url)
    response.raise_for_status()  # raises an error if the request failed

    general_track = {
        "track_type": "General",
        "internet_media_type": "application/vnd.apple.mpegurl",
        "format": "HLS"
    }
    video_track = {
    }
    sub_file=False
    for line in response.text.splitlines():
        if sub_file:
            stream_file = urljoin(url, line.strip())
            general_track['duration'] = get_hls_duration(stream_file)

        if "#EXT-X-STREAM-INF:" in line:
            match = re.search(r'RESOLUTION=(\d+)x(\d+)', line)
            if match:
                width, height = int(match.group(1)), int(match.group(2))
                video_track['track_type'] = 'Video'
                video_track['width'] = width
                video_track['height'] = height
            else:
                video_track['track_type'] = 'Audio'
            sub_file=True    

    return { "tracks": [ general_track, video_track] }

    
def get_hls_duration(m3u8_path):
    response = requests.get(m3u8_path)
    response.raise_for_status()

    content = response.text

    durations = re.findall(r'#EXTINF:([\d.]+),', content)
    total = sum(float(d) for d in durations)
    return total * 1000  # in miliseconds