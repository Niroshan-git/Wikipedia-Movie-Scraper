# Wikipedia Movie Scraper

## About The Project
A Streamlit-based web application that scrapes movie information from Wikipedia and enriches it with data from the OMDb API. This tool specializes in extracting comprehensive information about movie franchises and series, providing an intuitive interface for data collection and analysis.

![Capture](https://github.com/user-attachments/assets/56a5f5fc-b58c-473f-977e-3f513cd06e1f)


## Key Features

### 1. User Interface & Experience
- Clean, intuitive Streamlit interface
- Pre-configured popular movie franchise selections (MCU, DC, Star Wars, etc.)
- Interactive progress tracking with cancel capability
- Flexible scraping options (scrape all or specific number of movies)
- Real-time progress updates and error reporting

![List of films](https://github.com/user-attachments/assets/d04870c1-af64-453e-9431-44a250e4031f)

### 2. Data Collection & Integration
- **Wikipedia Data Extraction:**
  - Movie titles and basic information
  - Cast and crew details
  - Technical specifications
  - Box office performance
  - Production details
  
- **OMDb API Integration:**
  - IMDb ratings
  - Metascores
  - Rotten Tomatoes scores

### 3. Error Handling & Logging
- Comprehensive error logging system
- Separate logs for failed scrapes
- Real-time error display in UI
- Graceful handling of missing data
- 
![Error Handling](https://github.com/user-attachments/assets/177cef5d-4a66-4f6d-9d8f-3687549b8534)

### 4. Data Export
- CSV export functionality
- Clean, structured data format
- Comprehensive movie metadata
- Ready for analysis or database import

- ![CSV Download](https://github.com/user-attachments/assets/615089cd-6b80-4e9b-aab5-1c9d47185bc6)


## Technical Implementation

### Core Components
```python
- Web Scraping: BeautifulSoup4
- UI Framework: Streamlit
- API Integration: OMDb API
- Data Processing: Pandas
- Error Handling: Custom logging system
```

### Key Technical Features
1. **Robust Data Extraction**
   - Handles various Wikipedia page structures
   - Extracts data from infoboxes and tables
   - Image URL extraction and validation

2. **Data Standardization**
   - Runtime conversion to integers
   - List to string conversions
   - Consistent data formatting

3. **Error Management**
   - Failed scrapes logging
   - API request error handling
   - Data validation checks

## Getting Started

### Prerequisites
```bash
pip install streamlit pandas beautifulsoup4 requests python-dotenv
```

### Environment Setup
Create a `db.env` file with:
```
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=your_host
DB_PORT=your_port
DB_NAME=your_database_name
```

### Running the Application
```bash
streamlit run movie_scraper.py
```

## Outcomes & Applications

### Data Collection Capabilities
- Successfully scrapes complete movie franchise information
- Handles various Wikipedia page layouts
- Extracts comprehensive movie metadata
- Integrates ratings from multiple sources

### Use Cases
1. Film Research & Analysis
2. Movie Database Population
3. Franchise Comparison Studies
4. Content Management Systems
5. Movie Analytics Projects

## Future Improvements
1. Add support for more movie databases
2. Implement advanced error recovery
3. Add data visualization features
4. Expand franchise coverage
5. Implement batch processing capabilities

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


---
*Note: Remember to update the OMDb API key for your own use.*
