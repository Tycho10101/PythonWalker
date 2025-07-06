import PythonWalker as pw

import time
import random

EMAIL = "example@example.com" #CHANGE
PASSWORD = "password123" #CHANGE
WORLD_ID = "abcde12345" #CHANGE

eightball = [
            "It is certain", 
            "It is decidedly so", 
            "Without a doubt", 
            "Yes definitely", 
            "You may rely on it", 
            "As I see it, yes", 
            "Most likely", 
            "Reply hazy, try again", 
            "Ask again later", 
            "Better not tell you now", 
            "Cannot predict now", 
            "Concentrate and ask again", 
            "Don’t count on it", 
            "My reply is no", 
            "My sources say no", 
            "Outlook not so good", 
            "Very doubtful", 
            "Signs point to yes", 
            "Yes", 
            "Outlook good"
            ]

eat = [
      "guzzled a grape", 
      "chewed a cherry", 
      "ate an avocado", 
      "choked on a cheeseburger"
      ]

user = pw.login_with_pass(EMAIL, PASSWORD)

start_time = None

def is_integer(value, zero_included=False):
    if not isinstance(value, str):
        if isinstance(value, int):
            return True
        return False
    
    value = value.strip()
    if not value:
        return False
        
    if value.isdigit() and int(value) == 0 and not zero_included:
        return False
        
    return value.isdigit()
    
def on_init(conn, packet):
    global start_time
    global prefix
    start_time = time.time()
    conn.send_chat("Hello! I'm PWBot10101! Use \"//help\" for commands")

def on_join(conn, packet):
    global start_time
    global prefix
    if time.time() > start_time + 1:
        conn.send_chat("Welcome " + packet.properties.username + "! I'm PWBot10101! Use \"//help\" for commands")

def on_leave(conn, packet):
    conn.send_chat("Goodbye " + conn.players[packet.player_id] + "!")
    
def help(conn, args, player_id):
    if len(args) > 1:
        conn.send_chat("This command only needs atmost 1 argument")
        return

    if len(args) == 0:
        list = 1
    elif is_integer(args[0]):
        list = int(args[0])
    else:
        conn.send_chat("This command's argument needs to be an Integer above 0")
        return

    if list == 1:
        conn.send_chat("[//help 2 for more commands] Commands: | help (List #) | say [words] | roll [#1] [#2] | 8ball [Quesion] |")
    elif list == 2:
        conn.send_chat("[//help 3 for more commands] Commands: | wheel [Choices Separated by commas] | eat | players |")
    else:
        conn.send_chat("[//help for commands] No more commands")
        
def say(conn, args, player_id):
    if len(args) == 0:
        conn.send_chat("This command needs atleast 1 argument")
        return
    echo = " ".join(args).strip()
    if echo.startswith("/"):
        conn.send_chat('You may not start an echo with "/".')
        return
    conn.send_chat(echo)
    
def roll(conn, args, player_id):
    if not len(args) == 2:
        conn.send_chat("This command's arguments needs to be 2 integers")
        return
    if not is_integer(args[0].lstrip("-"), True):
        conn.send_chat("This command's arguments needs to be 2 integers")
        return
    if not is_integer(args[1].lstrip("-"), True):
        conn.send_chat("This command's arguments needs to be 2 integers")
        return
    if int(args[0]) > int(args[1]):
        conn.send_chat("The first argument is bigger than the second")
        return

    rand = random.randint(int(args[0]), int(args[1]))
    conn.send_chat("Rolled a " + str(rand) + " (" + args[0] + " to " + args[1] + ")")
    
def eightball_cmd(conn, args, player_id):
    global eightball
    if len(args) == 0:
        conn.send_chat("This command needs atleast 1 argument")
        return

    question = " ".join(args)
    answer = random.choice(eightball)

    conn.send_chat("Q: " + question + " A: " + answer)
    
def wheel(conn, args, player_id):
    if len(args) == 0:
        conn.send_chat("This command needs atleast 1 argument")
        return

    choices = " ".join(args).split(",")
    for i in range(len(choices)):
        choices = [choice.strip() for choice in choices]

    choice = random.choice(choices)
    conn.send_chat("The wheel has landed on: " + choice)
    
def eat_cmd(conn, args, player_id):
    global eat
    if not len(args) == 0:
        conn.send_chat("This command has no arguments")
        return
    food = random.choice(eat)

    conn.send_chat(conn.players[player_id] + " " + food)
    
def players_cmd(conn, args, player_id):
    playerlist = []
    for player in conn.players.values():
        playerlist.append(player)
    playerlist = "Players: " + ", ".join(playerlist)
    conn.send_chat(playerlist)
    
commands = {
           "help":help,
           "say":say,
           "roll":roll,
           "8ball":eightball_cmd,
           "wheel":wheel,
           "eat":eat_cmd,
           "players":players_cmd
           }

client = pw.connect(WORLD_ID, user, on_init=on_init, on_join=on_join, on_leave=on_leave, commands=commands)