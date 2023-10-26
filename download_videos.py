"""
A Johnware Project
2023
"""

# this program will download all the videos
# by reading the csv file and downloading each video

import csv
import os
import time
import tqdm


def download_video(video_url, video_name):
    """Downloads a video from a url and saves it to a file.

    Args:
      video_url: The url of the video to download.
      video_name: The name of the video file to save the video to.
    """

    # Import the requests module.
    import requests

    # Make a GET request to the video url.
    response = requests.get(video_url, stream=True)

    # Open the video file for writing in binary mode.
    with open(video_name, "wb") as video_file:
        # Iterate over the response content in 1KB chunks.
        for chunk in tqdm(response.iter_content(chunk_size=1024)):
            # Write the chunk to the file.
            video_file.write(chunk)


if __name__ == "__main__":
    # read in files
    with open("video_links.csv", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        i = 0
        for row in reader:
            video_url = row[0]
            video_name = f"video_{i}.mp4"
            print("Downloading video: " + video_name + " from url: " + video_url)
            download_video(video_url, video_name)
            print("Downloaded video: " + video_name)
            time.sleep(2)
            i += 1
