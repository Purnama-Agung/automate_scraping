# AUTOMATE WEB SCRAPING USING SELENIUM #
for everyone. maintained by Agung

# Requirements #
- Python3.8+
- Linux
- Selenium
- Xvfb

# Installation Tools on Ubuntu #
- sudo apt update
- sudo apt-get install build-essential && sudo apt-get install build-essential
- sudo apt-get install autoconf automake gdb git libffi-dev zlib1g-dev libssl-dev

# Webdriver Version #
[Optional] you can use firefox browser and geckodriver, but i'm using chrome
- Google Chrome Browser - at least 108.0.5359.124 do the same version for chromedriver
- Chrome install "curl --insecure https://intoli.com/install-google-chrome.sh | bash"
- Download same version of chromedriver as your's Chrome - try this https://chromedriver.storage.googleapis.com/index.html
- wget https://chromedriver.storage.googleapis.com/108.0.5359.71/chromedriver_linux64.zip && unzip chromedriver_linux64.zip
- sudo mv chromedriver /usr/bin/chromedriver && sudo chown root:root /usr/bin/chromedriver && sudo chmod +x /usr/bin/chromedriver

# Web Scraping Installation #
- pip install -r requirements.txt
- Note: please setup your connection using proxy malaysia