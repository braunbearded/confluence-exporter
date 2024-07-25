import requests
from requests.auth import HTTPBasicAuth
import json
from dotenv import load_dotenv
import os
import argparse
import logging
import sys

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

domain = os.getenv('DOMAIN')
auth_email = os.getenv('AUTH_EMAIL')
auth_token = os.getenv('AUTH_TOKEN')
depth = os.getenv('DEPTH', 'all')
sort = os.getenv('SORT', 'modified-date')
status = os.getenv('STATUS', 'current')
body_format = os.getenv('BODY_FORMAT', 'atlas_doc_format')
limit = int(os.getenv('LIMIT', 25))

auth = HTTPBasicAuth(auth_email, auth_token)

headers = {
  "Accept": "application/json"
}

def get_all_spaces(domain, auth):
   url = f"https://{domain}/wiki/api/v2/spaces"
   response = requests.request(
      "GET",
      url,
      headers=headers,
      auth=auth
   )
   all_spaces = json.loads(response.text)

   if not all_spaces or not all_spaces.get("results") or len(all_spaces["results"]) == 0:
      logger.error("Failed to retrieve spaces.")
      sys.exit(2)

   return all_spaces


def get_space_infos(space_name, spaces):
   space = next((result for result in spaces['results'] if result['name'] == space_name), None)
   if not space:
      logger.error(f"Couldn't find space {space_name}")
      sys.exit(3)
   return space

def get_pages_in_space(id, domain, auth, depth="all", sort="modified-date", status="current", title=None, body_format="atlas_doc_format", limit=25):
   url = f"https://{domain}/wiki/api/v2/spaces/{id}/pages"

   params = {
      'depth': depth,
      'sort': sort,
      'status': status,
      'title': title,
      'body-format': body_format,
      'limit': limit
   }

   params = {k: v for k, v in params.items() if v is not None}

   response = requests.request(
      "GET",
      url,
      headers=headers,
      auth=auth,
      params=params
   )
   pages = json.loads(response.text)
   if not pages or not pages.get("results") or len(pages["results"]) == 0:
      logger.error(f"Couldn't find pages")
      sys.exit(4)

   return pages

def save_pages(pages, space, output_dir):
   print(json.dumps(pages))

def main():
   parser = argparse.ArgumentParser(description="Get pages in a Confluence space.")
   parser.add_argument('output-dir', type=str, help="Name of directory to save pages to")
   parser.add_argument('--space', "-s", action="append", required=True, help="Name of space to export (can be used multiple times but at least once)")
   args = parser.parse_args()

   all_spaces = get_all_spaces(domain, auth)
   
   for space_name in args.space:
      space = get_space_infos(space_name, all_spaces)

      space_id = space["id"]

      pages = get_pages_in_space(space_id, domain, auth, depth=depth, sort=sort, status=status, body_format=body_format, limit=limit)

      save_pages(pages, space, getattr(args, "output-dir"))

if __name__ == "__main__":
    main()
