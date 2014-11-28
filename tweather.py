#!/usr/bin/env python
# -*- coding: utf-8 -*-
import serial
import tweepy 
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from tweepy.cursor import Cursor
import time
import numpy as np
import requests
import urllib2
from datetime import datetime


api_key = '845d3GVInIsKo5trbJ2GvGciX'  
api_secret = 'zcZUKm9m1ubrZigwFh51Qa9rn9g2TjmSwIAkk6bVODBlN9mBDX'
access_token = '2910840228-l9D3QgnBodWaXWHBqDJbMpm6Nj3e9fkIlTRK6mL'
access_secret = 'E8Q9GZrx6TuHFkVTouPPhNTMrKZT3wKTbfz04fvN7FMZR'

a = 17.271
b = 237.7 # degC

t_list = []

my_ip = urllib2.urlopen('http://ip.42.pl/raw').read()
url  = 'http://ip-api.com/json/' + my_ip
r = requests.get(url)
r = r.json()
location  = r['city'] + ", " + r['country']


def dewpoint_approximation(T,RH):
  Td = (b * gamma(T,RH)) / (a - gamma(T,RH))
  return Td

def gamma(T,RH):
  g = (a * T / (b + T)) + np.log(RH/100.0)
  return g
 

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

auth = OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)
pattern_weather_TH = [unicode("@tweather_bot สภาพอากาศเป็นอย่างไรบ้าง?", "utf-8"),
          unicode("@tweather_bot รายงานสภาพอากาศหน่อย", "utf-8"),
          unicode("@tweather_bot รายงานสภาพอากาศตอนนี้หน่อยซิ", "utf-8"),
          unicode("@tweather_bot เช็คสภาพอากาศตอนนี้หน่อย", "utf-8") ]

pattern_weather_EN = [u"@tweather_bot How is the weather now?"]

pattern_hello = [ unicode("@tweather_bot สวัสดี", "utf-8"),
          unicode("@tweather_bot หวัดดีจ้า", "utf-8"),
          unicode("@tweather_bot ดีจ้า", "utf-8")]

pattern_noob = [unicode("@tweather_bot แต่งงานกับผมเถอะ", "utf-8")]

t_list.append("537833844250914816")
t_list.append('537880632148246528')
t_list.append('537880476925427713')
t_list.append('538241563625660417')
t_list.append('538234016462151680')
t_list.append('538244064034828288')
t_list.append('538259952297447424')
t_list.append('538366224019623936')
t_list.append('538366626823811072')
t_list.append('538378051776561152')
t_list.append('538381741853913088')
t_list.append('538386031519600640')
t_list.append('538366502953426944')
t_list.append('538387788878450688')

while True :
  tweet = api.mentions_timeline()
  for t in tweet:
    print " Tweet ID: "+ str(t.id) + " <" + t.text + "> By [" + t.user.screen_name + "] \n" 
    if t.text in pattern_weather_EN and ( str(t.id) not in t_list) :
      time_data = datetime.now().strftime('%H:%M:%S')
      t_data = str(t.id)
      t_list.append(t_data)
      sn = t.user.screen_name
      sensor_data = sensor_reader(True).split()
      humidity = sensor_data[0]
      temperature = sensor_data[1]
      heat_index = sensor_data[2]
      dew_point = dewpoint_approximation(float(temperature),float(humidity))
      dew_point = '{0:.2f}'.format(dew_point)
      tweet_weather = "Humidity: " + humidity + ", " + "Temperature: " + temperature + " °C, " + "Heat index: " + heat_index + " °C, " + "Dew Point: "  + str(dew_point) +" °C"
      m = "@"+ sn + " (" + time_data + ") " + tweet_weather + " at " + str(location) 
      s = api.update_status(m, t.id)
      print "tweet is posted"

    if t.text in pattern_weather_TH and ( str(t.id) not in t_list) :
      time_data = datetime.now().strftime('%H:%M:%S')
      t_data = str(t.id)
      t_list.append(t_data)
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

    #print t_list

    if t.text in pattern_hello and ( str(t.id) not in t_list) :
      t_data = str(t.id)
      t_list.append(t_data)
      sn = t.user.screen_name
      m = "@"+ sn + unicode(" สวัสดีครับ :)", "utf-8")
      s = api.update_status(m, t.id)

      print "tweet is posted"

    if t.text in pattern_noob and ( str(t.id) not in t_list) :
      t_data = str(t.id)
      t_list.append(t_data)
      sn = t.user.screen_name
      m = "@"+ sn + unicode(" ตกลงค่ะ ฉันจะแต่งงานกับคุณ <3", "utf-8")
      s = api.update_status(m, t.id)
      print "tweet is posted"

  time.sleep(60)