<h1 align="center"><b>𝗤𝗨𝗘𝗘𝗡-𝗠𝗨𝗦𝗜𝗖 🎧</b></h1>

<p align="center">
  <img src="https://files.catbox.moe/f8i9s1.jpg" width="500"/>
</p>

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?color=FF00FF&width=620&lines=🍁+🎧+𝗣𝗢𝗪𝗘𝗥𝗘𝗗+𝗕𝗬+𝗤𝗨𝗘𝗘𝗡+𝗫+𝗠𝗨𝗦𝗜𝗖+🎧+🍁">
</p>

<h2 align="center">✨ Deploy Your Own Telegram Music Bot Easily! ✨</h2>

---

### 🌐 Deploy Method:

#### 🚀 Deploy on Heroku
[![Deploy to Heroku](https://img.shields.io/badge/Deploy%20On%20Heroku-green?style=for-the-badge&logo=heroku)](https://dashboard.heroku.com/new?template=https://github.com/ASIFXQUEEN903/RADHEXMUSICBOT)

---

### 💻 Manual VPS / Local Deploy:

```bash
# Update and upgrade packages
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install python3-pip ffmpeg -y
sudo pip3 install -U pip
curl -fssL https://deb.nodesource.com/setup_19.x | sudo -E bash - && sudo apt-get install nodejs -y && npm i -g npm

# Clone the bot
git clone https://github.com/ASIFXQUEEN/XQUEEN-MUSIC-903 && cd XQUEEN-MUSIC-903

# Install requirements
pip3 install -U -r requirements.txt

# Edit env
vi sample.env  # Press I to edit, Ctrl+C to exit, then :wq to save

# Rename env file
mv sample.env .env

# Use tmux to keep bot running
sudo apt install tmux && tmux

# Run the bot
bash start
