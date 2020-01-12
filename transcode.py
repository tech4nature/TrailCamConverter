
import logging
import subprocess
import pathlib
import json
from glob import glob
from datetime import datetime
from typing import Dict


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
    logging.basicConfig(filename='transcode.log', filemode='w', format=f'%(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)  # Setup logging
    state = deserialize()

    logging.info(f"Started")

    try:
        i = 0
        for file in [file for file in glob("**", recursive=True) if file[-3:].lower() == "avi"]:
            i += 1
            logging.info(f"Found: {file}")
            new_video = {
                "name": file.split("/")[-1][:-4],
                "path": pathlib.Path.cwd() / pathlib.Path(file),
                "modified_date": None,
                "transcoded": False,
                "posted": False,
                "box_id": file.split("/")[1],
                "id": i
            }

            # Check if already in state
            exists = False

            for video in state:
                if video["id"] == new_video["id"]:
                    logging.debug("Found Duplicate Video")
                    exists = True

            if not exists:
                state.append(new_video)

        # Pull Out Modified Date as JSON
        for video in state:
            if video["modified_date"] is None:
                cmd = ["exiftool", "-filemodifydate", "-j", video["path"]]
                modified_date = json.loads(subprocess.run(cmd, capture_output=True, check=True).stdout)[0]
                modified_date = modified_date["FileModifyDate"][:22] + \
                    modified_date["FileModifyDate"][23:]
                modified_date = datetime.strptime(
                    modified_date, "%Y:%m:%d %H:%M:%S%z").strftime("%Y-%m-%d-%H-%M-%S-%z")
                video["modified_date"] = modified_date
                video["name"] = modified_date
                logging.info(f"Pulled metadate from: {video['path']}, got: {video['modified_date']}")

        # Transcode Videos
        for video in state:
            if not video["transcoded"]:
                path = pathlib.Path().cwd() / ".transcoded" / \
                    video["box_id"] / (video["name"] + ".mp4")
                subprocess.run(["mkdir", path.parent.parent, path.parent])
                cmd = ["ffmpeg", "-i", str(video["path"]),
                       "-c:v", "libx264", "-preset", "slow", "-crf", "26", "-c:a", "mp3", "-r", "25", "-y", path]
                subprocess.run(cmd, check=True)
                logging.info(f"Transcoded: {video['path']}, now at: {path}")
                video["path"] = path
                video["transcoded"] = True

    except KeyboardInterrupt:
        serialize(state)
        logging.debug("Interrupted by user")

    except Exception as e:
        logging.error(e)

    serialize(state)
