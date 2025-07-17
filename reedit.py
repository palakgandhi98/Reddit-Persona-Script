import praw
import config
import requests # Import the requests library for making HTTP requests
import re
from urllib.parse import urlparse
import os

# Ensure you have a GEMINI_API_KEY in your config.py
# Example config.py:
# username = "your_reddit_username"
# password = "your_reddit_password"
# client_id = "your_reddit_client_id"
# client_secret = "your_reddit_client_secret"
# GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

# Initialize Reddit
reddit = praw.Reddit(username=config.username,
                      password=config.password,
                      client_id=config.client_id,
                      client_secret=config.client_secret,
                      user_agent="UserPersonaScript by Otherwise-Exam-5520")

def extract_username(profile_url):
    """
    Extracts the Reddit username from a given profile URL.
    """
    path = urlparse(profile_url).path
    return path.strip('/').split('/')[-1]

def fetch_user_content(username, limit=100):
    """
    Fetches posts and comments for a given Reddit username.
    """
    user = reddit.redditor(username)
    posts = []
    comments = []

    try:
        print(f"Fetching user submissions for u/{username}...")
        for submission in user.submissions.new(limit=limit):
            posts.append({
                'type': 'post',
                'subreddit': submission.subreddit.display_name,
                'title': submission.title,
                'text': submission.selftext,
                'url': f"https://www.reddit.com{submission.permalink}"
            })
        print(f"Fetched {len(posts)} posts.")

        print(f"Fetching user comments for u/{username}...")
        for comment in user.comments.new(limit=limit):
            comments.append({
                'type': 'comment',
                'subreddit': comment.subreddit.display_name,
                'text': comment.body,
                'url': f"https://www.reddit.com{comment.permalink}"
            })
        print(f"Fetched {len(comments)} comments.")

    except Exception as e:
        print(f"Error fetching user content: {e}")
    
    return posts + comments

def build_prompt(user_content):
    """
    Builds the prompt for the language model based on user's Reddit activity.
    Limits the content to avoid exceeding token limits.
    """
    entries = []
    for item in user_content:
        if item['type'] == 'post':
            # Format for posts
            text = f"Post in r/{item['subreddit']} titled '{item['title']}':\n{item['text']}\nURL: {item['url']}"
        else:
            # Format for comments
            text = f"Comment in r/{item['subreddit']}:\n{item['text']}\nURL: {item['url']}"
        entries.append(text)

    # Limit to 50 entries to manage token count for the prompt
    # Adjust this limit if you encounter consistent token overload issues
    prompt = (
        "You are an AI that builds detailed user personas based on Reddit activity.\n"
        "Here are the posts and comments by a Redditor. Analyze and generate a persona "
        "with the following format:\n"
        "- Age Estimate\n- Interests\n- Occupation (if possible)\n"
        "- Personality Traits\n- Political or Social Views (if any)\n- Writing Style\n"
        "- Most Visited Subreddits\n\n"
        "Cite each conclusion with the relevant content or URL.\n\n"
        "Reddit Activity:\n" + "\n\n".join(entries[:50])
    )
    return prompt

def generate_persona(prompt):
    """
    Generates a user persona using the Google Gemini API.
    """
    api_key = config.GEMINI_API_KEY
    # Using gemini-2.0-flash as requested
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1500 # Corresponds to max_tokens
        }
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        
        json_response = response.json()
        
        # Extract the generated text from the Gemini response structure
        if json_response and 'candidates' in json_response and len(json_response['candidates']) > 0:
            if 'content' in json_response['candidates'][0] and 'parts' in json_response['candidates'][0]['content'] and len(json_response['candidates'][0]['content']['parts']) > 0:
                return json_response['candidates'][0]['content']['parts'][0]['text']
            else:
                print("❌ Gemini API response structure unexpected: 'parts' not found.")
                return "Error: Could not generate persona (unexpected response structure)."
        else:
            print("❌ Gemini API response structure unexpected: 'candidates' not found or empty.")
            return "Error: Could not generate persona (no candidates)."

    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling Gemini API: {e}")
        return f"Error: Could not generate persona ({e})"
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return f"Error: Could not generate persona (unexpected error: {e})"


def save_persona(username, persona_text):
    """
    Saves the generated persona to a text file.
    """
    filename = f"user_persona_{username}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(persona_text)
    print(f"✅ Persona saved to {filename}")

def main(profile_url):
    """
    Main function to orchestrate the persona generation process.
    """
    username = extract_username(profile_url)
    print(f"🔍 Fetching data for u/{username}...")
    user_content = fetch_user_content(username)
    
    if not user_content:
        print("❌ No data found for user or an error occurred during fetching.")
        return

    print("Building prompt for Gemini API...")
    prompt = build_prompt(user_content)
    
    print("Generating persona using Gemini API...")
    persona_text = generate_persona(prompt)
    
    if "Error:" in persona_text:
        print(f"Failed to generate persona: {persona_text}")
    else:
        save_persona(username, persona_text)

# Example usage
if __name__ == '__main__':
    # This part of the code runs when the script is executed directly.
    # It prompts the user for a Reddit profile URL.
    reddit_profile_url = input("Enter Reddit profile URL: ").strip()
    main(reddit_profile_url)