# immo-eliza-scraping
[![forthebadge made-with-python](https://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)


## 🏢 Description

In this project, I create a scraper that builds a CSV file containing data for 10,000 houses from every region of Belgium. I scrape data from [Immoweb](https://www.immoweb.be/en/). In my project, I use an OOP approach, as well as the asyncio module for asynchronous link processing, and BeautifulSoup for scraping data from HTML pages.







![immo_logo](https://is1-ssl.mzstatic.com/image/thumb/Purple221/v4/f9/e5/3c/f9e53c99-f50b-3f13-b2b8-558d80c48783/AppIcon-0-0-1x_U007epad-0-0-0-85-220.png/1200x630wa.png)

## 📦 Repo structure

```
.
├──data/
    ├──links/
        ├──houselinks_for_postcode.json
    ├──raw_data_houses.json
    ├── houselinks_for_postcode.json
├──scraper
    ├──scraper.py
├── src/
│   ├── link_creator.py 
    ├──pipeline.py
├── .gitignore
├── main.py
├── maintest.csv
├── postal-codes.json
└── README.md
```

## 🛎️ Usage
1. Clone the repository to your local machine.



2 .To run the script, you can execute the `main.py` file from your command line:

    ```
    python main.py
    ```

3. The script creates an instance of the Pipeline class and builds the csv file with data for 10000 houses in Belgium.
   The resulting file is saved to chousen filepath in your root directory.
   One run of script takes aproximately 15 minutes.

```python
from src.pipeline import Pipeline
import time
start_time = time.localtime()
start = time.strftime("%H:%M:%S", start_time)
print(start)
pipeline = Pipeline()
pipeline.run(input('Enter name of csv file that you want to save'))
finish_time = time.localtime()
finish = time.strftime("%H:%M:%S", finish_time)
print(finish)
```
## ⏱️ Timeline

This project took tree days for completion.


## Sources

I used [Postal codes - Belgium](https://data.opendatasoft.com/explore/dataset/georef-belgium-postal-codes%40public/export/?location=7,50.51954,4.48177&basemap=jawg.streets) dataset from "Opendatasoft" web site.

