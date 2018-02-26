#!/usr/bin/python

import io
import shutil
from apiclient.discovery import build
from apiclient.discovery import build_from_document
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
#from oauth2client.tools import run_flow
import httplib2
import os
import sys
import csv
import pdb
import argparse


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyDJFA5UmNNPVVRt0ufaEeD4hOk-VvveSjw"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_channel_search(arguments):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=arguments.q,
    part="id,snippet",
    maxResults=arguments.max_results,
    type ="channel"
  ).execute()

  channels = []

  # append the search result into channels, and return channels
  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#channel":
      channels.append("%s" % (search_result["id"]["channelId"]))
  return channels

def youtube_video_search(options, arguments):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=arguments.q,
    part="id,snippet",
    channelId=options,
    maxResults=arguments.max_results
  ).execute()

  videos = []

  # append the search result into videos, and return videos
  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      videos.append("%s" % (search_result["snippet"]["title"]))
      videos.append("%s" % (search_result["id"]["videoId"]))
  return videos




CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"


# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:
   %s
with information from the APIs Console
https://console.developers.google.com

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))


# Authorize the request and store authorization credentials.
def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  # Trusted testers can download this discovery document from the developers page
  # and it should be in the same directory with the code.
  with io.open("youtube-v3-discoverydocument.json", "r", encoding="utf8") as f:
    doc = f.read()
    return build_from_document(doc, http=credentials.authorize(httplib2.Http()))

def get_replies(youtube, parent_id, video_id, video_title, target):
  try:
    results = youtube.comments().list(
      part = "snippet",
      parentId = parent_id,
      maxResults = 100,
      textFormat = "plainText"
    ).execute()
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    for item in results["items"]:
      ReplyId = item["id"]
      AuthorName = item["snippet"]["authorDisplayName"]
      authorChannelId = item["snippet"]["authorChannelId"]["value"]
      likeCount = item["snippet"]["likeCount"]
      reply = youtube.comments().list(
        part = "snippet",
        id = ReplyId,
        maxResults = 100,
        textFormat = "plainText"
      ).execute()
      time = item["snippet"]["publishedAt"]
      try:
        target.writerow([video_id, video_title.translate(non_bmp_map), "reply", ReplyId,
                         parent_id, AuthorName.translate(non_bmp_map), authorChannelId, '',
                         reply["items"][0]["snippet"]["textDisplay"].translate(non_bmp_map),
                         likeCount, time])
      except:
        pass
    return 1
  except:
    return 0
    pass
    
    

# Call the API's commentThreads.list method to store the existing comment threads into file target.
def get_comment_threads(youtube, video_id, video_title, target):
  try:
    results = youtube.commentThreads().list(
      part="snippet",
      videoId=video_id,
      maxResults=100,
      order = "relevance",
      textFormat="plainText"
    ).execute()
  
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    for item in results["items"]:
      comment = item["snippet"]["topLevelComment"]
      author = comment["snippet"]["authorDisplayName"]
      commentId = comment["id"]
      authorChannelId = comment["snippet"]["authorChannelId"]["value"]
      text = comment["snippet"]["textDisplay"]
      time = comment["snippet"]["publishedAt"]
      likeCount = comment["snippet"]["likeCount"]
      try:
        target.writerow([video_id, video_title.translate(non_bmp_map),
                         "comment", commentId,
                         video_id, author.translate(non_bmp_map),
                         authorChannelId, text.translate(non_bmp_map), '',
                         likeCount, time])
        if (0 == get_replies(youtube, commentId, video_id, video_title, target)):
          youtube = get_authenticated_service(args)
          get_replies(youtube, commentId, video_id, video_title, target)
      except:
        pass
    return 1
  except:
    return 0



if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--q', help='Search term', default='Google')
  parser.add_argument('--max-results', help='Max results', default=25)
  arguments = parser.parse_args()
  print arguments.q

  args = argparser.parse_args()
  print args


  youtube = get_authenticated_service(args)
  myfile = open("Feminism Comments4", 'w')
  target = csv.writer(myfile, delimiter='\t')
  target.writerow(["videoId", "Video Title", "Comment or Reply", 
		   "Id", "parentId", "authorDisplayName",
		   "authorChannelId", "Comment Content", 
		   "Reply Content", "likeCount", "publishedAt"])
  for channel in youtube_channel_search(arguments):
    VideoList = youtube_video_search(channel, arguments)
    for x in range(0, len(VideoList)-1, 2):
      try:
        video_title = VideoList[x]
        video_id = VideoList[x+1]
        if (0 == get_comment_threads(youtube, video_id, video_title, target)):
          youtube = get_authenticated_service(args)
          get_comment_threads(youtube, video_id, video_title, target)
      except HttpError as e:
        print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
        pass
  myfile.close()
  