Dependencies: praw, ffmpeg, ffprobe, youtube-dl, python3.5+
To install dependencies, install python normally, then in command prompt type "pip install <dependency>"
To run, open command prompt or terminal, navigate to the directory where you have the file (to do so, type "cd <directory_name>" as many times as needed, and "cd .." to go up a directory), and type "python script.py <subreddit>"
There are a list of optional parameters, which will be listed below. To include them, follow this format: "python script.py <subreddit> -<letter> <cooresponding_input> -<letter2> <cooresponding_input2> ...":

-p, period to get posts from: day, week, month, year (default day))
-s, minimum post score (default 5)
-l, target video length (default 600 seconds)
-c, maximum clip length (default 60 seconds)
-d, delete clips and video once finished (default true)
-a, allow clips with no audio (default false)
-u, upload file to youtube (default true)
-pr, upload as public, private, or unlisted (default private)
-r, rerun code every period (default true)

API setup:
Reddit:
https://github.com/reddit-archive/reddit/wiki/API

Youtube:
Go here
https://console.cloud.google.com/apis/dashboard
Then go to credentials and create an api key and an OAuth 2.0 Clients ID. Then, replace the client_id and client_secret fields in client_secrets.json with the information from this page, and delete all the files that end with oauth2.json.

Misc:
If doing with ffmpeg-concat (transition filters): When running the program, your computer will probably experience massive slowdowns when the program begins processing the videos and merging them with transitions. Also, you should have around 30GB of free space for a 10 minute video. By default, it doesn't use this.