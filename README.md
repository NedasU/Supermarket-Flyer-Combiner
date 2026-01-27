# Lithuanian Supermarket Discount Aggregator

A web application that combines and compares discounts from multiple supermarkets (Lithuania).
<img width="1920" height="926" alt="image" src="https://github.com/user-attachments/assets/1519852a-f1a0-4d1c-af39-ea4e27a5ea4f" />

## Tech Stack
### Frontend 
- React
- Vite
  
### Backend
- Node.js
- Express.js

### Data Scraping
- Python
- Requests
- Selenium
- webdriver
- BeautifulSoup4
- psycopg2
- python-dotenv
  
### Database
- PostgreSQL

### Styling
- TailwindCSS

## Features
- Combine discounts from 4 Major Supermarkets in Lithuania
- Filter discounts by stores
- Search for discounts
- Full List Searches
- Related-Text based searches for finding similar discounts
- Automatic scraper checker based on last_scraped_at or expired offers

## Getting Started

### Prerequisites
- Node.js (v18+)
- npm
- Python (v3.10+)
- PostgreSQL
- Google Chrome (Selenium)


### Python Scraper Setup
In order to get python scrapers to work, the installation of the following libraries must be 
installed via pip.

```bash
pip install -r requirements.txt
```

### Environment Variables
Inside the root folder, a .env file needs to be created in order to store sensitive data such as
PostgreSQL password:
**Do NOT commit this file to GitHub.**

Example:
POSTGRESQL_PASSWORD=your_password

See '.env.example' for reference.
### Project Structure

```
Discount_flyer_Combiner/
├── Discount_Combiner_backend/   # Express.js backend
├── Flyer_reader/                # Python scraping modules
├── discount_combiner_frontend/  # React frontend
├── .env                         # Environment variables
├── .gitignore
├── README.md
```
### Data Flow

1. Python Scraper
   - "csv_to_sql.py" calls individual scrapers to produce csv files.
   - Each individual scraper code filters data from web scraping
   - "csv_to_sql.py" normalises data converts the csv files to sql queries and executes them.
   - Saves to PostgreSQL
  
2. Backend (Express.js)
   - Performs check to see if discount offers in the database are up to date.
   - Calls scraper if outdated data
   - Listens for API calls from React
   - Queries PostgreSQL
   - Returns JSON data to React
  
3. Frontend (React)
   - Fetches API data
   - Renders results to user
  ```
React Frontend
      ||
      ||
      \/
Express Backend
      ||
      ||
      \/
PostgreSQL  <----- Python Scraper (collects & normalises data)
```
### Running Locally

All dependencies must be installed before running the program.

Steps to running Python scrapers:
```
cd Flyer_reader
pip install -r requirements.txt
```

Steps to running backend:
```
cd Discount_Combiner_backend
npm install
node index.js
```

Steps to running frontend:
```
cd discount_combiner_frontend
npm install
npm run dev
```

### Future Improvements
The current version of this project is an MVP (Minimum Viable product), hence not ready for
production level. The following areas could be improved on the next version of this project:

1. Design - This is a basic MVP version design to test if all features work. It does not
currently look modernised and could be improved to help improve user interaction and experience.

2. Filters - The current selection of filters contain only the ability to filter by stores.
Adding additional filters such as price, product category and many more can help improve UX.

3. Stores - Currently, this project scrapes only 4 stores (Maxima, Lidl, IKI, and RIMI),
however, adding more stores could potentially improve UX/UI as it provides a wider catalogue of
discounts that are accessible to the user.

4. Features - Adding additional features like saving products to a shopping cart for the user
to see could be a nice touch. Additionally, incorporating a total costs calculator could also
help improving UX/UI

### Limitations
- Scrapers are currently hard coded to their each supermarket website, so any changes to their
html structure can cause the scrapers to crash or perform poorly.
- Not production level ready (no Docker, no CI/CD, no rate limiting)
