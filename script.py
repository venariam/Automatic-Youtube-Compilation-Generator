# Dependencies: praw, ffmpeg, ffprobe, python3.5+
#
# Potential TODO list:
# Automate title/descriptions - take name of top reddit post, decides on descriptions/category/keywords beforehand and repeat - could include options like whether or not to automate creation of these, or to use serial
# Subscribe/link prev at the end of the video
# Order clips by upvotes?
# Upload to other platforms like facebook/instagram/tiktok?
# Include automatically include clipnames and timestamps in description?
#
# Testing command example: python script.py aww -p week -d False -u False -r False

import praw
import time
import datetime
import subprocess
import os
import shutil
import argparse
import glob
from datetime import datetime, timedelta
from upload_video import *

reddit = praw.Reddit(
    client_id="",
    client_secret="",
    user_agent="")

parser = argparse.ArgumentParser(
    description='Automatically scrape top video submissions on reddit and combine them')
parser.add_argument('subreddit', metavar='subreddit',
                    type=str, help='subreddit to scrape')
parser.add_argument('-p', '--period', type=str, default="day",
                    help='period to get posts from: day, week, month, year (default day)')
parser.add_argument('-s', '--score', type=int, default=5,
                    help='minimum post score (default 5)')
parser.add_argument('-l', '--length', type=int, default=600,
                    help='target video length (default 600 seconds)')
parser.add_argument('-c', '--clip', type=int, default=60,
                    help='maximum clip length (default 60 seconds)')
parser.add_argument('-d', '--delete', type=str, default="True",
                    help='delete clips and video once finished (default true)')
parser.add_argument('-a', '--audio', type=str, default="False",
                    help='allow clips with no audio (default false)')
parser.add_argument('-u', '--upload', type=str, default="True",
                    help='upload file to youtube (default true)')
parser.add_argument('-pr', '--private', type=str, default="private",
                    help='upload as public, private, or unlisted (default private)')
parser.add_argument('-r', '--repeat', type=str, default="False",
                    help='rerun code every period (default true)')

dict = {
    "day": 1,
    "week": 7,
    "month": 31, #don't want repeats
    "year": 366 #don't want repeats
}

#get top reddit submissions that are either a video or twitch tv clip
def get_reddit_top(subreddit):
    subreddit = reddit.subreddit(subreddit)
    submissions_list = []
    for submission in subreddit.top(args.period, limit=100):
        title = submission.title
        link = 'https://www.reddit.com' + submission.permalink
        if 'clips.twitch' in submission.url or 'v.redd.it' in submission.url or 'gfycat.com' in submission.url or 'streamable' in submission.url:
            if submission.score > args.score:
                submissions_list.append(
                    (title, link, submission.url, submission.score, ""))

        submissions_list.sort(key=lambda x: x[3], reverse=True)
    return submissions_list

#get last modified file in folder
def newest(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)

#get video length
def get_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return float(result.stdout)

#checks if video has audio
def has_audio(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=nb_streams", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return (round(float(result.stdout.decode('utf-8'))) == 2)

#old code using old ffmpeg-concat - better looking video but way too memory intensive
"""
#merge clips into single video
def concatenate():
    command = "ffmpeg-concat temp_effect1.mp4 "
    clip_list = glob.glob("*.mp4")
    clip_list.insert(0, "..\Resources\intro.mp4")
    clip_list.append("..\Resources\outro.mp4")
    clip_files = []
    for c in clip_list:
        clip = "temp" + str(clip_list.index(c) + 1) + ".ts"
        clip2 = "temp_effect" + str(clip_list.index(c) + 1) + ".mp4"
        os.system("ffmpeg -i " + c + " -filter_complex [0:v]scale=ih*16/9:-1,boxblur=luma_radius=min(h\,w)/20:luma_power=1:chroma_radius=min(cw\,ch)/20:chroma_power=1[bg];[bg][0:v]overlay=(W-w)/2:(H-h)/2,crop=h=iw*9/16 -vb 1000000K " + clip)
        os.system("ffmpeg -i " + clip + " -vf scale=1980:1050 " + clip2)
        if clip2 != "temp_effect1.mp4" and os.path.exists(clip2):
            clip_files.append(clip2)
    for c in clip_files:
        command += c + " "
    command += "--output output.mp4 --frame-format png"
    os.system(command)
"""

#combine video clips
def concatenate():
    command = "ffmpeg -i \"concat:"
    clip_list = glob.glob("*.mp4")
    #clip_list.insert(0, "..\Resources\intro.mp4")
    #clip_list.append("..\Resources\outro.mp4")
    clip_files = []
    for c in clip_list:
        clip = "temp" + str(clip_list.index(c) + 1) + ".ts"
        clip2 = "temp_effect" + str(clip_list.index(c) + 1) + ".ts"
        os.system("ffmpeg -i " + c +
                  " -filter_complex [0:v]scale=ih*16/9:-1,boxblur=luma_radius=min(h\,w)/20:luma_power=1:chroma_radius=min(cw\,ch)/20:chroma_power=1[bg];[bg][0:v]overlay=(W-w)/2:(H-h)/2,crop=h=iw*9/16 -vb 1000000K " + clip)
        os.system("ffmpeg -i " + clip +
                  " -vf scale=1920:1080 -vb 1000000K " + clip2)
        if os.path.exists(clip2):
            clip_files.append(clip2)
    for c in clip_files:
        command += c
        if clip_files.index(c) != len(clip_files) - 1:
            command += "|"
    command += "\" -c copy output.mp4"
    os.system(command)
    os.system("move output.mp4 ../Videos")

#main code
def main():
    subreddit = args.subreddit
    valid_submissions = get_reddit_top(subreddit)

    if not os.path.exists('Clips'):
        os.makedirs('Clips')
    os.chdir('Clips')

    current_length = 0
    target_video_length = args.length

    #get clips
    for submission in valid_submissions:
        try:
            print(*submission, sep='\n')
            if 'clips.twitch' in submission[2]:
                os.chdir('..')
                str = submission[2]
                str = str[24:]
                os.system("TwitchDownloader -m ClipDownload --id " +
                          str + " -o Clips\\" + str + "_og.mp4")
                os.system("TwitchDownloader -m ChatDownload --id " +
                          str + " -o Clips\\" + str + ".json")
                if subprocess.check_output("ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 Clips\\" + str + "_og.mp4")[0:9].decode('utf-8') == '1920x1080':
                    os.rename("Clips\\" + str + "_og.mp4", "Clips\\" + str + "_og_resize.mp4")
                else:
                    os.system("ffmpeg -i Clips\\" + str + "_og.mp4" + " -vf scale=1920:1080 -vb 1000000K Clips\\" + str + "_og_resize.mp4")
                os.system("TwitchDownloader -m ChatRender -i Clips\\" + str +
                          ".json -h 1080 -w 422 --framerate 30 --update-rate 0 --font-size 18 --background-color #ffffff --message-color 111111 -o Clips\\" + str + "_chat.mp4")
                os.system("ffmpeg -i Clips\\" + str + "_og_resize.mp4 -i Clips\\" + str +
                          "_chat.mp4 -filter_complex hstack -vsync 2 Clips\\" + str + "_combo.mp4")
                os.system("ffmpeg -i Clips\\" + str +
                          "_combo.mp4 -vf scale=1920:-2 -vb 1000000K Clips\\" + str + "_resize.mp4")
                os.system("ffmpeg -i Clips\\" + str +
                          "_resize.mp4 -vf \"pad=width=1920:height=1080:x=0:y=97:color=black\" -vb 1000000K Clips\\" + str + "_output.mp4")
                try:
                    os.remove("Clips\\" + str + "_og.mp4")
                except OSError:
                    pass
                os.remove("Clips\\" + str + "_resize.mp4")
                os.remove("Clips\\" + str + "_chat.mp4")
                os.remove("Clips\\" + str + "_combo.mp4")
                os.remove("Clips\\" + str + "_og_resize.mp4")
                os.remove("Clips\\" + str + ".json")
                os.chdir('Clips')
            else:
                print(submission[2])
                subprocess.run(["youtube-dl", "-w", submission[2]])
            latest_file_name = newest(".")

            if get_length(latest_file_name) > args.clip or (has_audio(latest_file_name) == False and args.audio == "False"):
                os.remove(latest_file_name)
            else:
                #if args.title/description doesn't exist, then put submission[0] aka most popular title as the title description, as long as its length not too long
                current_length += get_length(latest_file_name)
                if current_length >= target_video_length:
                    break
            print()
        except UnicodeEncodeError:
            continue

    #merge clips
    concatenate()

    #upload to youtube
    if args.upload == "True":
        args.file = "Videos\\output.mp4"
        args.title = ""
        args.description = ""
        args.keywords = ""
        args.category = "20"
        args.privacyStatus = args.private
        args.noauth_local_webserver = False
        args.logging_level = "INFO"
        args.auth_host_port = [8080, 8090]
        args.auth_host_name = "localhost"

        os.chdir('..')
        youtube = get_authenticated_service(args)
        try:
            initialize_upload(youtube, args)
        except HttpError as e:
            print("An HTTP error %d occurred:\n%s" %
                  (e.resp.status, e.content))
        os.chdir('Clips')

    os.chdir('..')
    #cleanup, mainly for repeat runs
    del valid_submissions
    if args.delete == "True":
        shutil.rmtree('Clips')


#wrapper to repeat infinitely
args = parser.parse_args()
if args.repeat == "True":
    while True:
        main()
        time.sleep(24.0 * 60.0 * 60.0 * dict[args.period])
else:
    main()
