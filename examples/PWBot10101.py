import PythonWalker as pw

import time
import random

prefix = "!"
prefixCommand = False
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

def on_chat(conn, packet):
    global prefix
    global prefixCommand
    message = packet.message
    splitc = message.strip().split(" ")
    if not message[0] == prefix:
        return
    if splitc[0] == prefix + "say":
        if len(splitc) == 1:
            conn.send_chat("This command needs atleast 1 argument")
            return
        echo = " ".join(splitc[1:]).strip()
        if echo.startswith("/"):
            conn.send_chat('You may not start an echo with "/".')
            return
        conn.send_chat(echo)

    elif splitc[0] == prefix + "help":
        if len(splitc) > 2:
            conn.send_chat("This command only needs atmost 1 argument")
            return

        if len(splitc) == 1:
            list = 1
        elif is_integer(splitc[1]):
            list = int(splitc[1])
        else:
            conn.send_chat("This command's argument needs to be an Integer above 0")
            return

        if list == 1:
            conn.send_chat(f"[{prefix}help 2 for more commands] Commands: | help (List #) | say [words] | roll [#1] [#2] | 8ball [Quesion] |")
        elif list == 2:
            conn.send_chat(f"[{prefix}help 3 for more commands] Commands: | wheel [Choices Separated by commas] | ({'Enabled' if prefixCommand else 'Disabled'}) prefix [prefix] |")
        elif list == 3:
            conn.send_chat(f"[{prefix}help 4 for more commands] Commands: | eat | players |")
        else:
            conn.send_chat(f"[{prefix}help for commands] No more commands")

    elif splitc[0] == prefix + "roll":
        if not len(splitc) == 3:
            conn.send_chat("This command's arguments needs to be 2 integers")
            return
        if not is_integer(splitc[1].lstrip("-"), True):
            conn.send_chat("This command's arguments needs to be 2 integers")
            return
        if not is_integer(splitc[2].lstrip("-"), True):
            conn.send_chat("This command's arguments needs to be 2 integers")
            return
        if int(splitc[1]) > int(splitc[2]):
            conn.send_chat("The first argument is bigger than the second")
            return

        rand = random.randint(int(splitc[1]), int(splitc[2]))
        conn.send_chat("Rolled a " + str(rand) + " (" + splitc[1] + " to " + splitc[2] + ")")
    elif splitc[0] == prefix + "8ball":
        if len(splitc) == 1:
            conn.send_chat("This command needs atleast 1 argument")
            return

        question = " ".join(splitc[1:])
        answer = random.choice(eightball)

        conn.send_chat("Q: " + question + " A: " + answer)
    elif splitc[0] == prefix + "wheel":
        if len(splitc) == 1:
            conn.send_chat("This command needs atleast 1 argument")
            return

        choices = " ".join(splitc[1:]).split(",")
        for i in range(len(choices)):
            choices = [choice.strip() for choice in choices]

        choice = random.choice(choices)
        conn.send_chat("The wheel has landed on: " + choice)
    elif splitc[0] == prefix + "prefix":
        if not prefixCommand:
            conn.send_chat("Command Disabled")
            return

        if not len(splitc) == 2:
            conn.send_chat("This command only needs 1 argument")
            return

        prefix = splitc[1]
        conn.send_chat("Prefix is now: " + prefix)
    elif splitc[0] == prefix + "eat":
        if not len(splitc) == 1:
            conn.send_chat("This command has no arguments")
            return
        food = random.choice(eat)

        conn.send_chat(conn.players[packet.player_id] + " " + food)
    elif splitc[0] == prefix + "players":
        playerlist = []
        for player in conn.players.values():
            playerlist.append(player)
        playerlist = "Players: " + ", ".join(playerlist)
        conn.send_chat(playerlist)
    else:
        conn.send_chat(f"Unknown command: {splitc[0]}")
    
def on_init(conn, packet):
    global start_time
    global prefix
    start_time = time.time()
    conn.send_chat("Hello! I'm PWBot10101! My prefix is \"" + prefix + "\". Use \"" + prefix + "help\" for commands")

def on_join(conn, packet):
    global start_time
    global prefix
    if time.time() > start_time + 1:
        conn.send_chat("Welcome " + packet.properties.username + "! I'm PWBot10101! My prefix is \"" + prefix + "\". Use \"" + prefix + "help\" for commands")

def on_leave(conn, packet):
    conn.send_chat("Goodbye " + conn.players[packet.player_id] + "!")
    
client = pw.connect(WORLD_ID, user, on_chat=on_chat, on_init=on_init, on_join=on_join, on_leave=on_leave)
