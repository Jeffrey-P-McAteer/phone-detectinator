#!/usr/bin/env python

# Script has 2 roles: to scan for
# new devices under /var/lib/misc/dnsmasq.leases
# and to serve a captive portal page on :80.
# The captive portal lets people who bring phones
# nearby turn off the alarm for their device.

# MUST have permission to bind to :80

import os
import sys
import subprocess
import time
import traceback
import threading

from http.server import HTTPServer, BaseHTTPRequestHandler

# holds ['ab:cd:ef:12:34:45']
macs_triggering_alarm = []

# Holds [(expire_timestamp, 'ab:cd:ef:12:34:45')]
ignored_macs = []

class CaptivePortalHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    global macs_triggering_alarm
    global ignored_macs

    # TODO allow a GET to /disengage-alarm to remove MAC
    # from macs_triggering_alarm, and add an entry that
    # expires in 5 minutes to ignored_macs


    self.send_response(200)
    self.end_headers()

    self.wfile.write(bytes("Please turn off the alarm by clicking the following button:", "utf-8"))



def run_http_server():
  httpd = HTTPServer(('0.0.0.0', 80), CaptivePortalHandler)
  httpd.serve_forever()

def do_detection_poll():
  global macs_triggering_alarm
  global ignored_macs

  macs_triggering_alarm = []

  with open('/var/lib/misc/dnsmasq.leases', 'r') as fd:
    contents = fd.read()
    for line in contents.splitlines():
      line = line.strip()
      if not line or len(line) < 3:
        continue

      mac = 'todo'
      ignore_this_mac = False
      for _, ignored_mac in ignored_macs:
        if mac == ignored_mac:
          ignore_this_mac = True
          break
      
      if ignore_this_mac:
        continue

      if not mac in macs_triggering_alarm:
        macs_triggering_alarm.append(mac)


  # Sound alarm if len(macs_triggering_alarm) > 0:
  if len(macs_triggering_alarm) > 0:
    # First lookup names by MAC from /opt/device_names.csv

    # espeak -v en-us+m3 --stdout "John Smith has brought a phone into the workplace" | aplay

    # This will run for ~8 seconds
    subprocess.run([
      'mpv', '/opt/alarm.mp3'
    ], check=False)



def main():
  http_server_t = threading.Thread(target=run_http_server, args=())
  http_server_t.start()
  while True:
    try:
      do_detection_poll()
    except:
      traceback.print_exc()
    
    time.sleep(3)

if __name__ == '__main__':
  main()

