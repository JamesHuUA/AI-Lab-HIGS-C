# AI Lab's H-Index Google Scholar Crawler

The AI Lab periodically publishes the H-Indexes of top MIS professors. A crucial tool for this is our H-Index Google Scholar web Crawler (HIGS-C). The following README file contains description on the capability of the HIGS-C and the contents of this repository.

## Capabilities
Currently, the HIGS-C has the following capabilities:

1. Iterating through a list of names, querying/searching of each the name on Google Scholars, and recording all scholars/H-indexes found
2. Skipping of any scholars not found. Each skip is also recorded. 
3. Random sleeping to decrease the chances of Captcha Activation
4. Indefinite crawl pause for manual Captcha solving 
5. Automatic resumption of crawling process upon Captcha solution. 
6. Recording of scholars potentially skipped because of Captcha for re-crawling.

## Content
The HIGS-C repository contains all necessary folders and files for operation:

- [Folder] **pages**: Folder containing saved Google Scholar search results. Advised to clear this out before each run.
- [Folder] **profiles**: Folder containing saved Google Scholar profile pages. Advised to clear this out before each run.
- [Folder] **results**: Folder containing the final crawled H-Indexes and the skipped scholars
- [File] **crawler.py**: Main executable python file.
- [File] **names.csv**: Example of how the list of names should be formatted. Replace this file with an updated list of the scholars-of-interest. Make sure to keep the Name header and the same format.
- [File] **requirements.txt**: The Python libraries needed for this script.  
- [File] **README.md**: Markdown file for this repository   
- [File] **geckodriver**: Webdriver for Firefox Web Crawling. The driver included is 0.34.0 for Linux x64. 

## Installation
Installation occurs through several steps:

1. Download this repository
2. Navigate to location and install requirements via PIP: 
	```bash
	pip install -r requirements.txt
	```
3. Visit [https://github.com/mozilla/geckodriver/releases/](https://github.com/mozilla/geckodriver/releases/) to download the latest, OS-specific FireFox driver.

## Usage
Provided files can already be used to run an example crawl. To run, execute the following command in the CMD or run crawler.py in your prefered IDE:

```bash
python crawler.py
```

Parameter variables are found in the `main()` function. Each parameter has right-offsetted comment and can be changed to modify the dataflow and crawling behavior of the HIGS-C. 

## Documentation
Extensive comments are written within crawler.py to aid with readability.

For further documentation, please visit the official documentation sites for the used libraries:
- [**BeautifulSoup**](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [**selenium**](https://www.selenium.dev/selenium/docs/api/py/)
- [**pandas**](https://pandas.pydata.org/docs/)
- [**tqdm**](https://tqdm.github.io/)

## Dissemination and Awknowledgement
For parties outside of the University of Arizona AI Lab, please email Brandi Gaulin at [brandig@arizona.edu](brandig@arizona.edu) to obtain permission for use. For any projects and publications, please include James Lee Hu, [Dr. Hsinchun Chen](https://eller.arizona.edu/people/hsinchun-chen), and the [University of Arizona AI Lab](https://eller.arizona.edu/departments-research/centers-labs/artificial-intelligence) in an awknowledgement in final project. 
