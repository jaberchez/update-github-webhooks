# update-github-webhooks.py

This script updates the old Jenkins Job url (job/ci-generic/buildWithParameters) of the webhook to the new one (generic-webhook-trigger/invoke). 

## How to use it
You must provide the following environment variables:
- GITHUB_USERNAME
- GITHUB_TOKEN
- WEBHOOK_URL_OLD
- WEBHOOK_URL_NEW

Then, you must set the file with the names of the GitHub repos, one by line. 
Blank lines and lines beginning with # are ignored

## Example
~~~
python3 update-github-webhooks.py -f /tmp/repos/github_repos.txt
~~~

If you want to save the result into a file, you can provide the optional argument [-o|--output]
~~~
python3 update-github-webhooks.py -f /tmp/repos/github_repos.txt --output /tmp/repos/output.log
~~~

## Using docker
~~~
docker build -t update-github-webhooks .
~~~
~~~
docker run --rm -it \
  -e GITHUB_USERNAME=username \
  -e GITHUB_TOKEN=token \
  -v /tmp/repos/github_repos.txt:/tmp/repos/github_repos.txt \
   update-github-webhooks -f /tmp/repos/github_repos.txt
~~~

~~~
docker rmi update-github-webhooks
~~~