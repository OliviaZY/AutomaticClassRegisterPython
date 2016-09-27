# AutomaticClassRegisterPython
# Description: 
Another go at a better and more reliable class register.
The script uses Selenium to autonomously navigate through the pages and enter data.

Currently supported browsers:  
  - PhantomJS             (Default)  
  - Mozilla Firefox

I have not tested other browsers; however, all Selenium supported browsers should be supported by the script.

This has been tested during the Fall 2016-2017 registration period. I was able to get into two classes with less than 6 available spots.

# How to Use: 
  1. Edit the `data.txt` file. Any text surrounded by "**" should be deleted and replaced with valid data.
  2. Make sure `data.txt` and `main.py` are in the same folder.
  3. Navigate to where `main.py` was saved in the command line.
  4. Execute `python main.py <optional: browser name>`
     - Current browser names: "phantom" and "firefox" without the quotes. The script does not care about casing.
     - **Warning:** PhantomJS is a headless browser with no visual feedback. Check the `confirmation.jpg` file to ensure if you have successfully registered. For those paranoid, I suggest staying away from the headless browser default.
  5. The script will execute and navigate to the registration page. If it is not yet 7:28 AM, the script will print the current time. If it is pass 7:28 AM, it will constantly refresh the page until registration is ready. Then, it will fill out the fields and submit.
  6. Once completed, a screenshot will be taken and saved in the root directory as `confirmation.jpg`. The browser will then close.
