# Reddit Persona Script
================================

A script to generate user personas based on Reddit activity using the Gemini API.

## Overview

This script takes a Reddit profile URL as input, fetches the user's posts and comments, and uses the Gemini API to generate a detailed persona.

## Features

* Generate a user persona with the following attributes:
  * Age Estimate
  * Interests
  * Occupation (if possible)
  * Personality Traits
  * Political or Social Views (if any)
  * Writing Style
  * Most Visited Subreddits
* Cite each conclusion with the relevant content or URL

## Installation

1. Install the necessary dependencies:
   ```bash
pip install praw requests
```
2. Make sure you have a `config.py` file in the same directory with the following structure:
   ```python
username = "your_reddit_username"
password = "your_reddit_password"
client_id = "your_reddit_client_id"
client_secret = "your_reddit_client_secret"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```
3. Replace the placeholders in `config.py` with your Reddit and Gemini API credentials.

## Usage

1. Run the script:
   ```bash
python reedit.py
```
2. Enter a Reddit profile URL when prompted.

## Code

You can find the code in the `reedit.py` file. The script uses the Reddit API to fetch user data and the Gemini API to generate a persona.

## Contributing

If you'd like to contribute or report an issue, please submit a pull request or open an issue on the repository.

## License

This script is released under the MIT License. See `LICENSE.txt` for details.

## Credits

* Reddit API for user data
* Gemini API for persona generation

## Requirements

* Python 3.x
* praw library for Reddit API interaction
* requests library for HTTP requests