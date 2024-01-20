from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# News API key (replace with your actual API key)
api_key = '669a282242674761bf01e790f9fe6520'

# Define the base URL of the News API
url = 'https://newsapi.org/v2/everything'

def format_date(date_str):
    # Parse the original date string to a datetime object
    date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')

    # Format the date to a more readable format, e.g., "December 15th, 2024"
    # %B - Full month name, %d - Day of the month, %Y - Year with century
    formatted_date = date_obj.strftime('%B %d, %Y')

    # Add suffix to day
    day = date_obj.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    
    return formatted_date.replace(f' {day},', f' {day}{suffix},')

@app.route('/', methods=['GET', 'POST'])
def index():
    articles = []
    if request.method == 'POST':
        # Define specific and combined topics related to Israel and Hamas
        topics = [
            '"Israel" AND "Hamas" AND conflict',
            # Add more specific topics as required
        ]

        # Combine topics with OR, each topic is enclosed in parentheses
        query = ' OR '.join(f'({topic})' for topic in topics)

        # Define the date range for the articles
        from_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')

        # Define the request parameters
        params = {
            'q': query,
            'from': from_date,
            'sortBy': 'relevancy',  # Sort by relevancy to get the most relevant articles for each topic
            'language': 'en',  # Assuming you want articles in English
            'apiKey': api_key
        }

        # Make the GET request
        response = requests.get(url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            raw_articles = response.json().get('articles', [])
            # Filter articles and format dates
            articles = [{'title': article['title'],
                         'description': article['description'],
                         'url': article['url'],
                         'publishedAt': format_date(article['publishedAt'])}
                        for article in raw_articles if not 
                        (article['title'] == '[Removed]' or 
                         article['description'] == '[Removed]' or 
                         article['publishedAt'] == '1970-01-01T00:00:00Z')]
        else:
            print(f"Failed to fetch articles. Status code: {response.status_code}")
            print(response.text)  # To see the error message from the API

    return render_template('index.html', articles=articles)

if __name__ == '__main__':
    app.run(debug=True)
