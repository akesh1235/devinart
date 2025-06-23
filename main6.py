# from fastapi import FastAPI
import webbrowser
import http.server
import socketserver
from urllib.parse import parse_qs, urlparse
from requests_oauthlib import OAuth1Session
import os
from dotenv import load_dotenv
# import uvicorn
load_dotenv()


# app = FastAPI()

# @app.get("/callback")
# def callback():
#     return {"message": "Hello World"}

# Replace with your actual Tumblr API keys
consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')

# Step 1: Get a request token
request_token_url = 'https://www.tumblr.com/oauth/request_token'
oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

# Fetch request token
fetch_response = oauth.fetch_request_token(request_token_url)
resource_owner_key = fetch_response.get('oauth_token')
resource_owner_secret = fetch_response.get('oauth_token_secret')

# Step 2: Authorize the request token
authorize_url = f'https://www.tumblr.com/oauth/authorize?oauth_token={resource_owner_key}'
print(f'Please go to this URL and authorize the app: {authorize_url}')


# Open the URL in the browser
webbrowser.open(authorize_url)

# Step 3: Set up a simple local HTTP server to handle the OAuth callback
class OAuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL to extract the oauth_verifier
        query = urlparse(self.path).query
        params = parse_qs(query)
        oauth_verifier = params.get('oauth_verifier', [None])[0]

        if oauth_verifier:
            print(f"OAuth Verifier: {oauth_verifier}")
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'You can now close this window. You have successfully authorized the app!')
            self.server.oauth_verifier = oauth_verifier
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Error: Missing oauth_verifier')

# Start the local HTTP server
# with socketserver.TCPServer(("localhost", 8000), OAuthHandler) as httpd:
#     print("Waiting for OAuth callback...")
#     httpd.handle_request()

# Step 4: Get the access token
oauth_verifier = input("Enter the OAuth verifier: ")#httpd.oauth_verifier  # Retrieved from the callback
if oauth_verifier:
    access_token_url = 'https://www.tumblr.com/oauth/access_token'
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret,
                          resource_owner_key=resource_owner_key,
                          resource_owner_secret=resource_owner_secret)
    
    # Exchange the oauth_verifier for the access token
    access_tokens = oauth.fetch_access_token(access_token_url, verifier=oauth_verifier)

    access_token = access_tokens.get('oauth_token')
    access_token_secret = access_tokens.get('oauth_token_secret')

    print("Access Token and Access Token Secret obtained!")

    # Step 5: Post to Tumblr
    blog_name = 'yourblogname'  # Replace with your blog name
    post_url = f'https://api.tumblr.com/v2/blog/{blog_name}.tumblr.com/post'

    # Content of the post
    title = 'My First Blog Post'
    body = '<h1>This is the body of the post</h1><p>It can contain HTML</p>'

    # Prepare the OAuth session with access tokens
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret,
                          resource_owner_key=access_token, resource_owner_secret=access_token_secret)

    # Post data
    data = {
        'title': title,
        'body': body,
        'format': 'html'  # Can be 'markdown' or 'plain' as well
    }

    # Make the POST request to create the blog post
    response = oauth.post(post_url, data=data)

    if response.status_code == 201:
        post_url = response.json()['response']['post']['url']
        print(f"Blog post successfully created! URL: {post_url}")
    else:
        print(f"Error creating post: {response.status_code} - {response.text}")

