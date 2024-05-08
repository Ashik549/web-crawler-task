# web-crawler-task

A web crawler for Adidas JP website which collects product info and store it on a spreadsheet.
Install the requirements first from requirements.txt and then run the main.py file to execute.


**"headless" crawling option is disabled as I coded this on macOS. Due to macOS optimizations, headless crawling can't collect dynamically loaded contents. Disabling headless option slows down the execution significantly. Please turn it on by commenting out the _# options.add_argument("--headless")_ statement in main function inside main.py file.**

The output spreadsheet file is inside the _dist/sheets_ directory.
