# Lecture Scraper

This tool allows for a student to download the lecture recordings for classes they have taken at the university.

## Usage

### Software Requirements

We use python3 with selenium for web-scraping. We will be using the Chrome Web driver so make sure you have the chrome browser installed. See [here](https://selenium-python.readthedocs.io/installation.html#drivers) for further instructions.

Install the project decencies:
[selenium](https://selenium-python.readthedocs.io/installation.html), [loguru](https://github.com/Delgan/loguru)

```
pip install -r requirements.txt
```

### Running the Lecture Scraper

Run and follow the instructions:

```
python3 scrape_from_leccap.py
```

The script will return a csv file of all the lecture recording links.

### Running the Lecture Download script

After running the above, if you want to download the lectures run the download script:

> [!NOTE]  
> This may take considerable time to run given the large video files.

```
python3 download_videos.py <path to csv file>
```

Where the csv file contains the links to the videos that were extracted using the `scrape_from_leccap.py` script.

## Demo

<i>Coming Soon...</i>

## License

[Apache 2 License](https://choosealicense.com/licenses/apache-2.0/) is used for this project.

This project is for educational purposes only.

At no point is this software or any of its creators liable for how the software is used. This includes using the tool to scrape and download lectures (the university has copyright over all lecture materials - and this tool in no way should be used to re-distribute such materials).

## Note to Developers

Find stable releases of the latest chromedriver here: [link](https://googlechromelabs.github.io/chrome-for-testing/#stable)

- using selenium version 4.6 and above we should not have to worry about drivers since they should automatically be downloaded

### Building Executables

To build the executable we use pyinstaller:

```
pyinstaller --name Lecap\ Scraper --icon=media/icon.icns --noconfirm --noconsole --onefile gui.py
```

On windows we need to use the `.ico` instead of the `.icns` app icon.

Unfortunately pyinstaller does not support cross-compilation so we will need to build the project on each target OS we want to make a release for.

> [!NOTE]
> To use the lecture scraper gui on linux you may need to install:
> ```
> sudo apt install libxcb-cursor0
> ```