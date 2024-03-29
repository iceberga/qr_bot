# qr_bot
A test project to create a bot for decrypting and creating QR codes on python and aiogram 3.4.1. 
It is my first telegram bot.
Project was developed for cafe's bonus programm. It is not a full version of code.

## Functional
1. Bot has 2 conditions: User and Admin.
2. User can register in bonus programm just sharing his phone number with bot. After registration he can check his status in bonus programm, send his purchase's check to bot and if he has enough purchases he can get his bonus via creating new qr-code by bot and show it to Admin.
3. Admin can register User's bonus by making a photo of generated qr-code. After it he will see on his screen the kind of bonus User got (for example, Сappuccino 300ml) and the user_id of User under it (this is necessary to write off the User's bonus)

## Instruction
1. After download the repository you have to make a folder named 'sql' in main project folder. This folder will contain a database with tables (I used SQLite). Also you need to recieve your own BOT_TOKEN via @BotFather and include it into config.ini (token = BOT_TOKEN).
2. To make user as Admin you need to add his user_id in admin_ids.

## Launch of the project
1. At first, you need to create virtual enviroment and activate it.
2. Install all necessary libs with command
```
pip list -r reqiurements.txt
```
3. Run
```
python bot.py
```
