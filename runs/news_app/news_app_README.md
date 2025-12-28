# Flask News App

A simple Flask application that allows users to get the latest news headlines from various countries and categories.

## Features

- Select news by country
- Filter by news category
- Responsive design
- Error handling
- Mock data for testing without API key

## Requirements

- Python 3.6+
- Flask
- Requests

## Installation

1. Make sure you have Python installed
2. Install the required packages:
   ```
   pip install flask requests
   ```

## Usage

1. Get an API key from [NewsAPI.org](https://newsapi.org/) (free for development)
2. Set your API key as an environment variable:
   ```
   # On Linux/Mac
   export NEWS_API_KEY=your_api_key_here
   
   # On Windows
   set NEWS_API_KEY=your_api_key_here
   ```
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
├── templates/
│   ├── index.html       # Home page with search form
│   ├── news.html        # News results page
│   └── error.html       # Error page
└── news_app_README.md   # This README file
```

## API Information

This application uses the [News API](https://newsapi.org/) to fetch the latest headlines. The free tier has some limitations:
- 100 requests per day
- No access to articles older than 1 month
- Limited to certain news sources

## License

This project is open source and available under the MIT License.