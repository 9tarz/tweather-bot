#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial, time, MySQLdb , tweepy
from tweepy import Stream
from tweepy import OAuthHandler
import requests, urllib2
from datetime import datetime
from dew_point_calculator import *

api_key = ''  
api_secret = ''
access_token = ''
access_secret = ''

PATTERN_WEATHER_TH = [unicode("@tweather_bot สภาพอากาศเป็นอย่างไรบ้าง?", "utf-8"),
          unicode("@tweather_bot รายงานสภาพอากาศหน่อย", "utf-8"),
          unicode("@tweather_bot รายงานสภาพอากาศตอนนี้หน่อยซิ", "utf-8"),
          unicode("@tweather_bot เช็คสภาพอากาศตอนนี้หน่อย", "utf-8"),
          unicode("@tweather_bot สภาพอากาศเป็นอย่างไรบ้าง?", "utf-8")]

PATTERN_WEATHER_EN = [u"@tweather_bot How is the weather now?", 
          u"@tweather_bot How about weather in my room?"]

PATTERN_TEMPERATURE_EN = [u"@tweather_bot How about temperature?"]

PATTERN_HUMIDITY_EN = [u"@tweather_bot How about humidity?"]

PATTERN_HELLO_TH = [ unicode("@tweather_bot สวัสดี", "utf-8"),
          unicode("@tweather_bot หวัดดีจ้า", "utf-8"),
          unicode("@tweather_bot ดีจ้า", "utf-8")]

PATTERN_TIME_TH = [ unicode("@tweather_bot ตอนนี้กี่โมงแล้ว", "utf-8"),
          unicode("@tweather_bot กี่โมงแล้ว", "utf-8"),
          ]

PATTERN_INTRODUCE_TH = [ unicode("@tweather_bot เธอชื่ออะไรเหรอ?", "utf-8"),
          unicode("@tweather_bot เธอชื่ออะไรเหรอ", "utf-8"),
          unicode("@tweather_bot อยากรู้จักเธอจัง", "utf-8"),
          ]


def sensor_reader(cmd = False):
    ser = serial.Serial('/dev/ttyUSB0', 9600) # Establish the connection on a specific port
    counter = 32 # Below 32 everything in ASCII is gibberish
    while True:
      counter +=1
      ser.write(str(chr(counter))) # Convert the decimal number to ASCII then send it to the Arduino
      if cmd == True:
        return ser.readline() # Read the newest output from the Arduino
      #sleep(.1) # Delay for one tenth of a second
      if counter == 255:
        counter = 32

def writeReplyedTweetIDtoMySQL(tweet_id):
  x = db.cursor()
  try:
    x.execute("INSERT INTO `tweatherbot`.`replyedtweet`(`id`, `tweet_id`) VALUES ( NULL" + ", '" + tweet_id + "');")
    db.commit()
  except:
    db.rollback()

def readReplyedTweetIDfromMySQL(tweet_id):
  x = db.cursor()
  x.execute("SELECT tweet_id FROM `tweatherbot`.`replyedtweet` WHERE tweet_id = " + "'" + tweet_id + "';")
  result = x.fetchone()
  if result == None:
    return ()
  return result

def replyedTweet_WEATHER_EN(PATTERN_WEATHER_EN, tweet_id):
  if t.text in PATTERN_WEATHER_EN and tweet_id not in readReplyedTweetIDfromMySQL(tweet_id):
    time_data = datetime.now().strftime('%H:%M:%S')
    writeReplyedTweetIDtoMySQL(tweet_id)
    sn = t.user.screen_name
    sensor_data = sensor_reader(True).split()
    humidity = sensor_data[0]
    temperature = sensor_data[1]
    heat_index = sensor_data[2]
    dew_point = dewpoint_approximation(float(temperature),float(humidity))
    dew_point = '{0:.2f}'.format(dew_point)
    tweet_weather = "Humidity: " + humidity + ", " + "Temperature: " + temperature + " °C, " + "Heat index: " + heat_index + " °C, " + "Dew Point: "  + str(dew_point) +" °C"
    m = "@"+ sn + " Time: " + time_data + " " + tweet_weather + " at " + str(location) 
    s = api.update_status(m, t.id)
    print "tweet is posted"

def replyedTweet_WEATHER_TH(PATTERN_WEATHER_TH, tweet_id):
  if t.text in PATTERN_WEATHER_TH and tweet_id not in readReplyedTweetIDfromMySQL(tweet_id) :
    time_data = datetime.now().strftime('%H:%M:%S')
    writeReplyedTweetIDtoMySQL(str(t.id))
    sn = t.user.screen_name
    sensor_data = sensor_reader(True).split()
    humidity = sensor_data[0]
    temperature = sensor_data[1]
    heat_index = sensor_data[2]
    dew_point = dewpoint_approximation(float(temperature),float(humidity))
    dew_point = '{0:.2f}'.format(dew_point)
    tweet_weather = "ความชื้นสัมพัทธ์: " + humidity + ", " + "อุณหภูมิ: " + temperature + " °C, " + "ดัชนีความร้อน: " + heat_index + " °C, " + "จุดน้ำค้าง: "  + str(dew_point) +" °C"
    m = "@"+ sn + " เวลา " + time_data + " " + tweet_weather + " จาก " + str(location) 
    s = api.update_status(m, t.id)
    print "tweet is posted"

def replyedTweet_HELLO_TH(PATTERN_HELLO_TH, tweet_id):
  if t.text in PATTERN_HELLO_TH and tweet_id not in readReplyedTweetIDfromMySQL(tweet_id) :
    writeReplyedTweetIDtoMySQL(str(t.id))
    sn = t.user.screen_name
    m = "@"+ sn + unicode(" สวัสดีค่ะ :)", "utf-8")
    s = api.update_status(m, t.id)
    print "tweet is posted"

def replyedTweet_TIME_TH(PATTERN_TIME_TH, tweet_id):
  if t.text in PATTERN_TIME_TH and tweet_id not in readReplyedTweetIDfromMySQL(tweet_id) :
    H_time = datetime.now().strftime('%H')
    M_time = datetime.now().strftime('%M')
    S_time = datetime.now().strftime('%S')
    writeReplyedTweetIDtoMySQL(str(t.id))
    sn = t.user.screen_name
    tweet_text_reply =  " ขณะนี้เวลา " + H_time + " นาฬิกา " + M_time +" นาที " + S_time + " วินาทีค่ะ" 
    m = "@"+ sn + unicode(tweet_text_reply, "utf-8")
    s = api.update_status(m, t.id)
    print "tweet is posted"

def replyedTweet_TEMPERATURE_EN(PATTERN_TEMPERATURE_EN, tweet_id):
  if t.text in PATTERN_TEMPERATURE_EN and tweet_id not in readReplyedTweetIDfromMySQL(tweet_id):
    time_data = datetime.now().strftime('%H:%M:%S')
    writeReplyedTweetIDtoMySQL(tweet_id)
    sn = t.user.screen_name
    sensor_data = sensor_reader(True).split()
    temperature = sensor_data[1]
    tweet_weather = "Temperature: " + temperature + " °C"
    m = "@"+ sn + " (" + time_data + ") " + tweet_weather + " at " + str(location) 
    s = api.update_status(m, t.id)
    print "tweet is posted"

def replyedTweet_HUMIDITY_EN(PATTERN_HUMIDITY_EN, tweet_id):
  if t.text in PATTERN_HUMIDITY_EN and tweet_id not in readReplyedTweetIDfromMySQL(tweet_id):
    time_data = datetime.now().strftime('%H:%M:%S')
    writeReplyedTweetIDtoMySQL(tweet_id)
    sn = t.user.screen_name
    sensor_data = sensor_reader(True).split()
    humidity = sensor_data[0]
    tweet_weather = "Humidity: " + humidity
    m = "@"+ sn + " (" + time_data + ") " + tweet_weather + " at " + str(location) 
    s = api.update_status(m, t.id)
    print "tweet is posted"

def replyedTweet_INTRODUCE_TH(PATTERN_INTRODUCE_TH, tweet_id):
  if t.text in PATTERN_INTRODUCE_TH and tweet_id not in readReplyedTweetIDfromMySQL(tweet_id) :
    writeReplyedTweetIDtoMySQL(str(t.id))
    sn = t.user.screen_name
    m = "@"+ sn + unicode(" สวัสดีค่ะ เราชื่อ Tweather Bot เป็นบอทรายงานสภาพอากาศผ่าน Twitter ยินดีที่ได้รู้จักน่ะค่ะ :)", "utf-8")
    s = api.update_status(m, t.id)
    print "tweet is posted"


my_ip = urllib2.urlopen('http://ip.42.pl/raw').read()
url  = 'http://ip-api.com/json/' + my_ip
r = requests.get(url)
r = r.json()
location  = r['city'] + ", " + r['country']


auth = OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

db = MySQLdb.connect("localhost","root","123456789","tweatherbot" )

while True :
  tweet = api.mentions_timeline()
  for t in tweet:
    print " Tweet ID: "+ str(t.id) + " <" + t.text + "> By [" + t.user.screen_name + "] \n" 

    tweet_id = str(t.id)
    print readReplyedTweetIDfromMySQL(tweet_id)

    replyedTweet_WEATHER_EN(PATTERN_WEATHER_EN, tweet_id)

    replyedTweet_WEATHER_TH(PATTERN_WEATHER_TH, tweet_id)

    replyedTweet_HELLO_TH(PATTERN_HELLO_TH, tweet_id)

    replyedTweet_TIME_TH(PATTERN_TIME_TH, tweet_id)

    replyedTweet_TEMPERATURE_EN(PATTERN_TEMPERATURE_EN, tweet_id)

    replyedTweet_HUMIDITY_EN(PATTERN_HUMIDITY_EN, tweet_id)

    replyedTweet_INTRODUCE_TH(PATTERN_INTRODUCE_TH, tweet_id)

  time.sleep(60)