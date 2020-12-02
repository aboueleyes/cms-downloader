# CMS-downloader
A CLI python script that downloads the material of any course hosted on the  cms website for *UNIX-Like operating systems*

# Showcase

[![asciicast](https://asciinema.org/a/DMyCpZoJii6v7gOrT5J5B9ufA.svg)](https://asciinema.org/a/DMyCpZoJii6v7gOrT5J5B9ufA)


# Installation
install dependencies for Debian-based distros
```bash
$ sudo apt install wget chromium-chromedriver git
```
install dependencies for Arch-based distros
```bash
$ sudo pacman -Sy wget git chromedriver 
```
clone this repo 
```bash
$ git clone https://github.com/aboueleyes/cms-downloader.git
$ cd cms-downloader/
$ sudo pip3 install -r requirements.txt

```
You should edit cms-downloader file  according to your courses , username and password
```python
courses = {"course_name" , "another_one", ...}
Links = {
  "course_name" : "course_link"
}
username ="yourusername"
password = "yourpassword"
```
The script by deafult download in the ~/Downloads you can change it 
```python
os.chdir("path")
```
if you want to orgnaise your downloads you can make use of the variable *course*
```python
os.chdir("/home/user/semseter-3/"+course)
```

# Usage
```bash

$ chmod 755 ./cms-downloader
$ ./cms-downloader
```
Tip : you can use regular expressions in search </br>
to select more than option press \<tab\>
# DISCLAIMER
This script is not official. It is simply a personal script shared  for educational purposes only. 

