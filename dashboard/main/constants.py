from dashboard.settings import SERVICE_ENDPOINT


SURVEILLANCE_ENDPOINTS = {
    'FACE_MASK_DETECTION': '/video_feed',
    'CROWD_COUNTING': '/cvideo_feed',
    'SOCIAL_DISTANCING': '/svideo_feed',
    'SPEED_MONITORING': '/spvideo_feed',
    'BLACKLIST': '/black_video_feed'
}


ADD_CRIMINAL_API = SERVICE_ENDPOINT + '/add'
FACE_SEARCH_API = SERVICE_ENDPOINT + '/upload'
BLACKLIST_API = SERVICE_ENDPOINT + '/blacklist_criminal'
DEEPFAKE_DETECTION_API = SERVICE_ENDPOINT + '/deepfake'
