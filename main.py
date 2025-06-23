import os
import uvicorn
import requests
from requests_oauthlib import OAuth2Session
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
load_dotenv()
# Replace these with your actual client_id and client_secret
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
redirect_uri = 'http://localhost:8000/callback'

# OAuth2 endpoints
authorization_base_url = 'https://www.deviantart.com/oauth2/authorize'
token_url = 'https://www.deviantart.com/oauth2/token'

# FastAPI app setup
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Create OAuth2 session
oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)

# @app.get("/", response_class=HTMLResponse)
# async def home(request: Request):
#     # Step 1: Generate the authorization URL
#     authorization_url, state = oauth.authorization_url(authorization_base_url)
#     # Redirect the user to DeviantArt authorization page
#     return templates.TemplateResponse("index.html", {"request": request, "authorization_url": authorization_url})

@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def home(request: Request):
    # Step 1: Generate the authorization URL
    authorization_url, state = oauth.authorization_url(authorization_base_url)
    # Redirect the user to DeviantArt authorization page
    return templates.TemplateResponse("index.html", {"request": request, "authorization_url": authorization_url})


@app.get("/callback")
async def callback(request: Request):
    # Step 2: Capture the 'code' from the URL parameters
    authorization_code = request.query_params.get('code')
    if not authorization_code:
        raise HTTPException(status_code=400, detail="Authorization code not found in the callback URL.")
    
    # Step 3: Exchange the authorization code for an access token
    try:
        oauth.fetch_token(token_url, client_secret=client_secret, authorization_response=str(request.url))
        access_token = oauth.token['access_token']

        # Step 4: Create the journal
        create_journal_url = 'https://www.deviantart.com/api/v1/oauth2/deviation/journal/create'
        journal_data = {
            'title': 'My Journal Title',
            'content': 'This is the content of my journal post.'
        }

        # Add the access token to the request headers
        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        # Create the journal by making a POST request to the endpoint
        response = requests.post(create_journal_url, headers=headers, data=journal_data)

        if response.status_code == 200:
            return {"message": "Journal created successfully!", "data": response.json()}
        else:
            return {"error": response.status_code, "message": response.text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during token fetching or journal creation: {str(e)}")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
