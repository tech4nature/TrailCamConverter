import logging
import requests
from requests.auth import HTTPBasicAuth


HOGHOST = "http://trinity-stroud.hedgehogrepublic.org"
AUTH = HTTPBasicAuth(input("Enter Username: "), input("Enter Password: "))


logger = logging.getLogger(__name__)


def create_location(code, name):
    data = {"code": code, "name": name}

    return requests.post(HOGHOST + "/api/locations/", data=data, auth=AUTH).json()


def _create_measurement(
    location_id, measurement_type, time, measurement=None, hog_id=None
):
    data = {
        "hog_id": hog_id,
        "measurement_type": measurement_type,
        "observed_at": time.isoformat(),
        "location_id": location_id,
    }
    if measurement is not None:
        data["measurement"] = measurement

    response = requests.post(HOGHOST + "/api/measurements/", data=data, auth=AUTH)
    response.raise_for_status()
    return response.json()


def create_weight(location_id, hog_id, weight, time):
    return _create_measurement(location_id, "weight", time, weight, hog_id)


def create_inside_temp(location_id, temp, time):
    return _create_measurement(location_id, "in_temp", time, temp)


def create_outside_temp(location_id, temp, time):
    return _create_measurement(location_id, "out_temp", time, temp)


def upload_video(location_id, hog_id, video_path, time):
    measurement = _create_measurement(location_id, "video", time, hog_id=hog_id)
    logger.debug(measurement)
    measurement_id = measurement["id"]
    files = {"video": open(video_path, "rb")}
    url = HOGHOST + "/api/measurements/{}/video/".format(measurement_id)
    response =  requests.put(url, files=files, auth=AUTH)
    response.raise_for_status()
    print(response.text)
