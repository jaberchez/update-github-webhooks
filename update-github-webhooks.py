#! /usr/bin/python3

###################################################################################################################
# Description: Update GitHub Webhooks
###################################################################################################################

# Imports
#------------------------------------------------------------------------------------------------------------------
import os
import sys
import re
import signal
import json
import requests
import getopt
#------------------------------------------------------------------------------------------------------------------

# Variables
#------------------------------------------------------------------------------------------------------------------
webhook_url_old_str       = None
webhook_url_new_str       = None

username                  = None
token                     = None

repos_file                = None
output_file               = None

webhook_url_old_regex     = None
webhook_url_new_regex     = None

blank_line_regex          = re.compile(r'^$')
comment_line_regex        = re.compile(r'^#')
#------------------------------------------------------------------------------------------------------------------

# Functions
#==================================================================================================================
# Description: Handle signals
# Parameters:  Signal and frame of the object
# Return:      Nothing, just exit

def signal_handler(sig, frame):
   name_signal = ''

   if sig == 2:
      name_signal = "SIGINT"
   elif sig == 15:
      name_signal = "SIGTERM"
   else:
      name_signal = "UNKNOWN"

   output("\nCatch signal: " + name_signal)
   sys.exit(1)
#==================================================================================================================

#==================================================================================================================
# Description: Show how to use this script
# Parameters:  None
# Return:      Nothing, just exit

def usage():
   print("Usage: {} <-f|--file repos_file.txt> [-o|--output file_output.log] [-h|--help]".
          format(os.path.basename(sys.argv[0])))
   sys.exit(1)
#==================================================================================================================

#==================================================================================================================
# Description: Update GitHub repo
# Parameters:  Repo
# Return:      Nothing

def update_github_repo(github_repo):
   global username
   global token

   cab        = '#' * 80
   url_github = 'https://api.github.com'
   
   output(cab)
   output("Repo: {}".format(github_repo))

   try:
      r = requests.get("{}/search/repositories?q={}".format(url_github, github_repo), auth=(username,token))

      if r.status_code == 200:
         json_str = json.dumps(r.json())
         res      = json.loads(json_str)

         if 'total_count' in res:
            if res['total_count'] == 0:
               output("Webhook updated: False")
               output("Reason: Repo was not found")
               output(cab + "\n")

               return
      else:
         output("Webhook updated: False")
         output("Reason: {}".format(r.text))
         output(cab + "\n")

         return

      # Get webhooks
      r = requests.get("{}/repos/{}/{}/hooks".format(url_github, username, github_repo), auth=(username,token))

      if r.status_code == 200:
         json_str = json.dumps(r.json())
         res      = json.loads(json_str)

         for r in res:
            if 'id' in r:
               webhook_id = r['id']
            else:
               output("Webhook updated: False")
               output("Reason: \"id\" tag not found in response")
               output(cab + "\n")

               return

            if not 'config' in r:
               output("Webhook updated: False")
               output("Reason: \"config\" tag not found in response")
               output(cab + "\n")

               return

            if not 'url' in r['config']:
               output("Webhook updated: False")
               output("Reason: \"url\" tag not found in response")
               output(cab + "\n")

               return

            url_webhook = r['config']['url']

            if len(url_webhook) > 0:
               if webhook_url_new_regex.match(url_webhook):
                  # Webhook is already updated
                  output("Webhook updated: False")
                  output("Reason: Webhook is already updated")
                  output(cab + "\n")

                  return
               elif webhook_url_old_regex.match(url_webhook):
                  # Old webhook
                  url_webhook = re.sub(webhook_url_old_str, webhook_url_new_str, url_webhook)

                  payload = json.dumps({
                     'config': {
                        'url': url_webhook
                     }
                  })

                  # PATCH /repos/:owner/:repo/hooks/:hook_id
                  resp = requests.patch("{}/repos/{}/{}/hooks/{}".format(url_github, username, github_repo, webhook_id), 
                                        data=payload, auth=(username,token))

                  if resp.status_code == 200:
                     output("Repo webhook updated: True")
                     output(cab + "\n")

                     return
                  else:
                     output("Repo webhook updated: False")
                     output("Reason: {}".format(resp.text))
                     output(cab + "\n")

                     return

      output("Repo webhook updated: False")
      output("Reason: Webhook not found")
      output(cab + "\n")
   except Exception as e:
      print("[ERROR] Problems updating webhook {}".format(e))
      print(cab + "\n")
#==================================================================================================================

#==================================================================================================================
# Description: Write message to standard output and file (if it is configured)
# Parameters:  Message
# Return:      Nothing

def output(message):
   global output_file

   f = None

   print("{}".format(message))

   if output_file != None:
      try:
         f = open("{}".format(output_file), "a")
         f.write("{}\n".format(message))
      except:
         pass
      finally:
         f.close()
#==================================================================================================================

# Main
#******************************************************************************************************************
if __name__ == '__main__':
   # Catch signals
   signal.signal(signal.SIGTERM, signal_handler)
   signal.signal(signal.SIGINT,  signal_handler)

   if len(sys.argv) == 1:
      usage()

   # Get environment variables
   username            = os.getenv("GITHUB_USERNAME", None)
   token               = os.getenv("GITHUB_TOKEN",    None)
   webhook_url_old_str = os.getenv("WEBHOOK_URL_OLD", None)
   webhook_url_new_str = os.getenv("WEBHOOK_URL_NEW", None)
   
   try:
      opts, args = getopt.getopt(sys.argv[1:],"hf:o:",["help","file=", "output="])
   except getopt.GetoptError:
      usage()

   for opt, arg in opts:
      if opt in ("-h", "--help"):
         usage()
      elif opt in ("-f", "--file"):
         repos_file = arg
      elif opt in ("-o", "--output"):
         output_file = arg

   if not os.path.isfile(repos_file):
      print("[ERROR] File \"{}\" not found".format(repos_file))
      sys.exit(1)
   elif os.stat(repos_file).st_size == 0:
      print("[ERROR] File \"{}\" is empty".format(repos_file))
      sys.exit(1)

   if username == None:
      print("[ERROR] Environment variable \"GITHUB_USERNAME\" not found")
      sys.exit(1)

   if token == None:
      print("[ERROR] Environment variable \"GITHUB_TOKEN\" not found")
      sys.exit(1)

   if webhook_url_old_str == None:
      print("[ERROR] Environment variable \"WEBHOOK_URL_OLD\" not found")
      sys.exit(1)

   if webhook_url_new_str == None:
      print("[ERROR] Environment variable \"WEBHOOK_URL_NEW\" not found")
      sys.exit(1)

   webhook_url_old_regex = re.compile(r'.*{}.*'.format(webhook_url_old_str))
   webhook_url_new_regex = re.compile(r'.*{}.*'.format(webhook_url_new_str))

   try:
      f = open(repos_file, "r")

      for line in f:
         # Remove all spaces
         line = re.sub(r'\s+','', line)

         # Skip blank and comment lines
         if blank_line_regex.match(line) or comment_line_regex.match(line):
            continue

         update_github_repo(line)
   except Exception as e:
      print("[ERROR] {}".format(e))
      sys.exit(1)
#******************************************************************************************************************