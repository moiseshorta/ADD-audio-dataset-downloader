### Simple script for downloading n-hours of music from youtube,
### based on a list of music genres.
### @hexorcismos, 2023

import os
import sys
import time
from tinytag import TinyTag
from pytube import YouTube
from moviepy.editor import *
from youtube_search import YoutubeSearch
from tqdm import tqdm

# Callback function for progress updates during video download
def progress_callback(stream, chunk, bytes_remaining):
    global progress_bar
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    progress_bar.update(len(chunk))

# Download video from YouTube given a URL and an output path
def download_video(url, output_path):
    try:
        global progress_bar
        print(f"Downloading: {url}")
        yt = YouTube(url, on_progress_callback=progress_callback)
        video = yt.streams.filter(file_extension='mp4').get_highest_resolution()

        progress_bar = tqdm(total=video.filesize, unit='B', unit_scale=True, ncols=100)
        video.download(output_path=output_path)
        progress_bar.close()

        return os.path.join(output_path, video.default_filename)
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

# Convert video file to .wav format with 48kHz sample rate
def convert_to_wav(video_path, output_path):
    try:
        video = VideoFileClip(video_path)
        audio = video.audio
        wav_filename = os.path.splitext(video_path)[0] + ".wav"

        # Ensure the output directory exists
        os.makedirs(output_path, exist_ok=True)

        audio.write_audiofile(os.path.join(output_path, wav_filename), fps=48000)
        return wav_filename
    except Exception as e:
        print(f"Error converting to wav: {e}")
        return None

# Search for YouTube videos given a genre and max number of results
def search_videos(genre, max_results=5):
    search_results = YoutubeSearch(f"{genre} music", max_results=max_results).to_dict()
    return [f"https://www.youtube.com{result['url_suffix']}" for result in search_results]

# Main function to download music by genre and save it in .wav format
def main():
    # Get user input
    genres = input("Enter a list of genres separated by commas: ").split(',')
    output_path = input("Enter the output directory for the .wav files: ")
    hours_per_genre = float(input("Enter the number of hours you want to download for each genre: "))

    max_duration_per_genre = hours_per_genre * 60 * 60  # Convert hours to seconds

    # Iterate through each genre
    for genre in genres:
        genre = genre.strip()
        genre_output_path = os.path.join(output_path, genre)
        os.makedirs(genre_output_path, exist_ok=True)

        genre_duration = 0

        print(f"Searching for {genre} music on YouTube...")

        youtube_links_file = os.path.join(genre_output_path, 'youtube_links.txt')

        # Download videos until the desired duration is reached
        while genre_duration < max_duration_per_genre:
            video_urls = search_videos(genre, max_results=20)

            for url in video_urls:
                video_path = download_video(url, genre_output_path)
                if video_path:
                    wav_path = convert_to_wav(video_path, genre_output_path)
                    if wav_path:
                        duration = TinyTag.get(wav_path).duration
                        genre_duration += duration

                        # Save the YouTube link to the .txt file
                        with open(youtube_links_file, 'a') as f:
                            f.write(f"{url}\n")

                        # Delete the video file
                        os.remove(video_path)

                    # Check if the desired duration has been reached
                    if genre_duration >= max_duration_per_genre:
                        print(f"Reached {hours_per_genre} hours of {genre} music. Stopping download for this genre.")
                        break
if __name__ == "__main__":
    while True:
        main()
        print("Waiting for the next request...")
        time.sleep(5)
