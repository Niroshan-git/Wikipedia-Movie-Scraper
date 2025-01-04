import streamlit as st
import pandas as pd
import json
import logging
import urllib.parse
from bs4 import BeautifulSoup as bs
import requests
import os
import urllib
from io import StringIO
import re

# Setting up logging
logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Configure logging to append logs to existing file and reset when scraping starts
def setup_logging(log_file, level=logging.INFO):
    logging.basicConfig(
        filename=log_file,
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="a"  # Append to the log file
    )
    logger = logging.getLogger()
    return logger

# Call this function before each scraping session
logger = setup_logging("scraper.log")
failed_logger = setup_logging("failed_scrapes.log", logging.WARNING)

def get_omdb_info(title):
    base_url = "https://www.omdbapi.com/"
    api_key = ""
    parameters = {"apikey": api_key, 't': title}
    full_url = base_url + '?' + urllib.parse.urlencode(parameters)
    
    response = requests.get(full_url)
    
    logging.info(f"OMDb API response for {title}: Status Code: {response.status_code}")

    if response.status_code == 200:
        try:
            movie_data = response.json()
            if movie_data.get("Response", "False") == "False":
                logging.warning(f"OMDb API did not find the movie '{title}'. Error: {movie_data.get('Error')}")
                return None
            return movie_data
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON for {title}: {e}")
            return None
    else:
        logging.error(f"Failed OMDb API request for {title}. Status Code: {response.status_code}")
        return None

def get_rotten_tomato_score(omdb_info):
    ratings = omdb_info.get('Ratings', [])
    for rating in ratings:
        if rating['Source'] == 'Rotten Tomatoes':
            return rating['Value']
    return None

def get_info_box(url):
    page = requests.get(url)
    soup = bs(page.text, "html.parser")
    info_box = soup.find(class_="infobox vevent")
    if info_box:
        info_rows = info_box.find_all("tr")
        movie_info = {}
        for index, row in enumerate(info_rows):
            if index == 0:
                movie_info['Title'] = row.find("th").get_text(" ", strip=True)
                # Extract image URL
                img_tag = row.find("img")
                if img_tag:
                    logging.info(f"Found img tag: {img_tag}")
                    img_src = img_tag.get('src')
                    if img_src:
                        if img_src.startswith('//'):
                            img_src = 'https:' + img_src
                        movie_info['Image URL'] = img_src
                        logging.info(f"Image URL found: {img_src}")
                    else:
                        logging.warning("img tag found but no src attribute")
                        movie_info['Image URL'] = 'No src attribute in img tag'
                else:
                    logging.warning("No img tag found in the first row of infobox")
                    movie_info['Image URL'] = 'No image found'
            elif index == 1:
                continue
            else:
                th = row.find("th")
                td = row.find("td")
                if th and td:
                    content_key = th.get_text(" ", strip=True)
                    content_value = get_content_value(td)
                    movie_info[content_key] = content_value
        
        logging.info(f"Scraped movie info: {movie_info}")
        return movie_info
    else:
        logging.warning(f"No infobox found for URL: {url}")
        return None

def get_content_value(row_data):
    for citation in row_data(["sup", "span"]):
        citation.decompose()

    if row_data.find("li"):
        return [li.get_text(" ", strip=True).replace("\xa0", " ") for li in row_data.find_all("li")]
    else:
        return row_data.get_text(" ", strip=True).replace("\xa0", " ")

def minutes_to_integer(running_time):
    if running_time == 'N/A':
        return None

    if isinstance(running_time, list):
        entry = running_time[0]
        return int(entry.split(" ")[0])
    
    else:
        return int(running_time.split(" ")[0])

def extract_category(url):
    match = re.search(r"List_of_(.+?)_films", url)
    if match:
        category = match.group(1).replace("_", " ")
        return category
    return "Movies"

# Function to convert lists to strings
def convert_lists_to_strings(movie_data):
    for movie in movie_data:
        for key, value in movie.items():
            if isinstance(value, list):
                movie[key] = ", ".join(value)  # Convert list to comma-separated string
    return movie_data

def scrape_movies(url, num_to_scrape=None):
    url_all = requests.get(url)
    soup = bs(url_all.content, "html.parser")
    base_path = "https://en.wikipedia.org"
    movies = soup.select(".wikitable i a")

    if num_to_scrape is not None:
        movies = movies[:num_to_scrape]

    movie_info_list = []
    error_list = []
    total_movies = len(movies)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    cancel_button = st.button("Cancel Scraping")

    for index, movie in enumerate(movies):
        if cancel_button:
            st.warning(f"Scraping cancelled. {index} items processed.")
            break

        try:
            relative_path = movie['href']
            full_path = base_path + relative_path
            title = movie['title']

            status_text.text(f"Scraping {index + 1}/{total_movies}: {title}")
            
            logging.info(f"Scraping movie: {title}, URL: {full_path}")
            movie_info = get_info_box(full_path)

            if movie_info:
                logging.info(f"Successfully scraped info for {title}")
                movie_info['Running time (int)'] = minutes_to_integer(movie_info.get("Running time", 'N/A'))
                
                omdb_info = get_omdb_info(title)
                if omdb_info:
                    movie_info['imdbRating'] = omdb_info.get("imdbRating", None)
                    movie_info['Metascore'] = omdb_info.get("Metascore", None)
                    movie_info['Rotten Tomatoes'] = get_rotten_tomato_score(omdb_info)
                else:
                    logging.warning(f"OMDb data not found for: {title}")

                movie_info_list.append(movie_info)
            else:
                error_msg = f"Could not find info box for: {title}"
                logging.warning(error_msg)
                failed_logger.warning(error_msg)
                error_list.append({"title": title, "error": error_msg})

        except Exception as e:
            error_msg = f"Error scraping movie: {movie.get_text()} - {str(e)}"
            logging.error(error_msg)
            failed_logger.error(error_msg)
            error_list.append({"title": movie.get_text(), "error": str(e)})

        progress_bar.progress((index + 1) / total_movies)

    status_text.text("Scraping complete!" if not cancel_button else "Scraping cancelled.")
    return movie_info_list, error_list

def get_similar_urls():
    return {
        "Marvel Cinematic Universe": "https://en.wikipedia.org/wiki/List_of_Marvel_Cinematic_Universe_films",
        "DC Extended Universe": "https://en.wikipedia.org/wiki/List_of_DC_Extended_Universe_films",
        "Star Wars": "https://en.wikipedia.org/wiki/List_of_Star_Wars_films",
        "James Bond": "https://en.wikipedia.org/wiki/List_of_James_Bond_films",
        "Harry Potter": "https://en.wikipedia.org/wiki/List_of_Harry_Potter_films",
        "Fast & Furious": "https://en.wikipedia.org/wiki/List_of_Fast_%26_Furious_films",
        "Mission: Impossible": "https://en.wikipedia.org/wiki/Mission:_Impossible_(film_series)",
        "Jurassic Park": "https://en.wikipedia.org/wiki/List_of_Jurassic_Park_films",
        "The Lord of the Rings": "https://en.wikipedia.org/wiki/The_Lord_of_the_Rings_(film_series)",
        "Pirates of the Caribbean": "https://en.wikipedia.org/wiki/Pirates_of_the_Caribbean_(film_series)",
        "Disney Animated Films" :  "https://en.wikipedia.org/wiki/List_of_Disney_theatrical_animated_feature_films",
         "Martial Art Films": "https://en.wikipedia.org/wiki/List_of_martial_arts_films"
    }

def main():
    st.title("Movie Scraper")

    # Display similar URLs in the sidebar
    st.sidebar.header("Popular Movie Lists")
    similar_urls = get_similar_urls()
    selected_franchise = st.sidebar.selectbox("Choose a franchise", list(similar_urls.keys()))
    if selected_franchise:
        st.sidebar.write(f"URL: {similar_urls[selected_franchise]}")
        if st.sidebar.button("Use Selected URL"):
            st.session_state.url = similar_urls[selected_franchise]

    # Main content area
    url = st.text_input("Enter Wikipedia URL for movies", 
                        value=st.session_state.get('url', "https://en.wikipedia.org/wiki/List_of_Marvel_Cinematic_Universe_films"))

    if url:
        category = extract_category(url)
        st.header(f"{category} Movies")

    if st.button("Prepare Scraping"):
        if not url.startswith("https://en.wikipedia.org/"):
            st.error("Please enter a valid Wikipedia URL.")
        else:
            url_all = requests.get(url)
            soup = bs(url_all.content, "html.parser")
            movies = soup.select(".wikitable i a")
            total_movies = len(movies)

            st.session_state.total_movies = total_movies
            st.session_state.url = url
            st.write(f"Number of movies to scrape: {total_movies}")

    if 'total_movies' in st.session_state:
        num_to_scrape = st.number_input("Number of movies to scrape (default is all)", 
                                        min_value=1, max_value=st.session_state.total_movies, value=st.session_state.total_movies)

        if st.button("Start Scraping"):
            movie_data, errors = scrape_movies(url, num_to_scrape=num_to_scrape)

            if movie_data:
                # Convert any list-type values into strings before creating a DataFrame
                movie_data = convert_lists_to_strings(movie_data)
                
                df = pd.DataFrame(movie_data)
                st.write("Scraping Complete!")
                st.dataframe(df)

                # Add this line to check the columns
                st.write(f"Columns in the DataFrame: {df.columns.tolist()}")

                # Ensure 'Image URL' is included in the CSV
                if 'Image URL' not in df.columns:
                    st.warning("'Image URL' column is missing from the data.")
                
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name=f'{category}_movies.csv',
                    mime='text/csv',
                )

            if errors:
                st.write(f"Number of errors: {len(errors)}")
                st.write(errors)

if __name__ == "__main__":
    main()