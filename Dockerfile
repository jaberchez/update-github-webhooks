FROM python:3.7.7-slim

RUN pip3 install requests

COPY update-github-webhooks.py /usr/local/bin/update-github-webhooks.py
RUN chmod +x /usr/local/bin/update-github-webhooks.py

ENTRYPOINT [ "python3", "/usr/local/bin/update-github-webhooks.py" ]