import logging
import pathlib
import json
from datetime import datetime
from typing import Dict
import client


def deserialize():
    state = json.load(open("state.json", "r"))
    for video in state:
        video["path"] = pathlib.Path(video["path"])

    return state


def serialize(state: Dict):
    for video in state:
        video["path"] = str(video["path"])
    json.dump(state, open("state.json", "w"))


if __name__ == "__main__":
    logging.basicConfig(filename='post.log', filemode='w', format=f'%(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)  # Setup logging
    state = deserialize()

    logging.info(f"Started")

    try:
        # Post Videos
        while len(state) != 0:
            for video in state:
                if not video["posted"]:
                    client.upload_video(video["box_id"], "hog-outside", str(video["path"]),
                                        datetime.strptime(video["modified_date"], "%Y-%m-%d-%H-%M-%S-%z"))
                    video["posted"] = True
                    logging.info(f"Posted: {video['path']}")
                    state.remove(video)

    except KeyboardInterrupt:
        serialize(state)
        logging.debug("Interrupted by user")

    except Exception as e:
        logging.error(e)

    serialize(state)
