# Flask News App

A Flask application that allows users to get the latest news headlines from various countries and categories, with search functionality and pagination.

## Features

- Browse top headlines by country and category
- Search for news articles by keywords
- Pagination for browsing through multiple results
- Responsive design for mobile and desktop
- Caching to reduce API calls and improve performance
- Error handling and logging
- Mock data for testing without API key

## Requirements

- Python 3.6+
- Flask
- Requests
- Flask-Caching
- python-dotenv

## Installation

1. Clone the repository or download the source code
2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
4. Copy the `.env.example` file to `.env` and add your API key:
   ```
   cp .env.example .env
   ```
5. Edit the `.env` file and add your NewsAPI key

## Usage

1. Get an API key from [NewsAPI.org](https://newsapi.org/) (free for development)
2. Set your API key in the `.env` file or as an environment variable
3. Run the application:
   ```
   python news_app.py
   ```
4. Open your browser and navigate to `http://127.0.0.1:5000/`

## Testing Without API Key

If you don't provide an API key, the application will use mock data for testing purposes.

## Project Structure

```
news_app/
├── news_app.py          # Main Flask application
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
├── templates/
│   ├── index.html       # Home page with search form
│   ├── news.html        # News results page
│   └── error.html       # Error page
└── README.md            # This README file
```

## API Information

This application uses the [News API](https://newsapi.org/) to fetch the latest headlines. The free tier has some limitations:
- 100 requests per day
- No access to articles older than 1 month
- Limited to certain news sources

## Future Enhancements

- User authentication for personalized news feeds
- Saving favorite articles
- Email notifications for news on specific topics
- Advanced filtering options
- Dark mode toggle

## License

This project is open source and available under the MIT License.