# cms-downloader
A CLI python script that downloads the material of any course hosted on the  cms website (for UNIX-Like operating systems)
*This script is personal I just wanted to share*
## Showcase

[![asciicast](https://asciinema.org/a/K1QAHRyrFyj2Hzulc0y8KXrYa.svg)](https://asciinema.org/a/K1QAHRyrFyj2Hzulc0y8KXrYa)


# Installation
install dependencies for debian-based distros
```bash
sudo apt instsall xclip python3-tk python3-dev chromium-chromedriver 
sudo pip3 install tqdm iterfzf selenium pyautogui clipboard 
mkdir Downloads/{Math,CS,DE,English,Circuts}
```
You should edit the file according to your courses , username and password
```python
usernme ="yourusername"
paswword = "yourpassword"
```
Hint : you can use regular expressions in search 
to selct more thahhn option press tab
# Usage
```bash
chmod 755 ./cms-downloader
sudo ln -s ./cms-downloader /usr/bin/cms-downloader 
cms-downloader
```
