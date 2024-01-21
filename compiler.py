from sys import exit
from math import trunc
from random import randint

# get the code firstly
with open("code.ratcl", "r") as f:
    lines = [line.strip().split(" ") for line in f]

# make the code one line and seperated by spaces (ca -aii -aoi)
code = " ".join([" ".join(line) for line in lines]).split(" ")

stacks = {} # starts empty, so you have to create one yourself every time
output = ""
line = 0
cmdIndex = 0

def error(flavorText="Yeah, idk, maybe read the error type?"):
    global stacks, output, line
    print(f"\nERROR:\n  line/command {line + 1}\n    {code[line]}\n{flavorText}\n\nStacks (up to the point of error): {stacks}\n")
    exit()

while line < len(code):
    try:
        while cmdIndex < len(code[line]):
            cmd = code[line][cmdIndex]
            
            # Get* the left and right side parameters
            # * Tries to get the left and right side parameters
            try:
                lParam = code[line][cmdIndex - 1]
                rParam = code[line][cmdIndex + 1]
            except IndexError:
                lParam, rParam = "", ""
            
            # REAL COMMAND CHECKING WHOOOOO
            match cmd:

                # this one's important, it skips the next command. you'll understand when you actually try to use this lol
                case "-":
                    cmdIndex += 2
                    continue


                # STACK MANIPULATION

                case "c": # >> stackName >>
                    if rParam: # checks if empty string
                        stacks[rParam] = []
                    else:
                        error("parameterError/missingRequired. So, just letting you know, you have to name your stack. That's why you can have multiple stacks.")

                    cmdIndex += 2
                    continue

                case "r": # >> stackName >>
                    if rParam in stacks:
                        del stacks[rParam]
                    else:
                        error("stackError/notFound: Speaks for itself. You tried to remove a stack that doesn't even exist.")

                    cmdIndex += 2
                    continue

                case "p": # << stack << | >> value >>
                    if lParam in stacks:
                        try:
                            num = int(rParam, 16)
                            stacks[lParam].append(num)
                        except ValueError:
                            error("valueError/outOfRange: Ok. The push command supports values from 0 to F. You got that? Now fix your code and try it again.")

                    else:
                        error("stackError/notFound: Yeah, good luck pushing a value onto a nonexistent stack. Ever heard of the 'c' command?")

                    cmdIndex += 2
                    continue

                case "\"": # >> stack >> [entire next line gets pushed onto the stack left to right]
                    if rParam not in stacks:
                        error("stackError/notFound: Nonexistent stack. That's all I have to say.")

                    if line + 1 < len(code):
                        next_line = code[line + 1]
                        for char in next_line:
                            stacks[rParam].append(ord(char))
                        cmdIndex = 0
                        line += 2  # increment line by 2 to skip the next line
                        continue
                    else:
                        error("valueError/endOfFile: You're trying to use the \" command, which reads the next line. Guess what? You don't even have a next line. Pat yourself on the back for this one.")

                case "'": # >> stack >> [just push a space. why not?]
                    if rParam in stacks:
                        stacks[rParam].append(32)
                    else:
                        error("stackError/notFound: Pushing a space to nothing. Nice.")
                        
                    cmdIndex += 2
                    continue

                case "s": # << stack << | >> sub cmd >> [looks through for one of the subcmds and does that]
                    if lParam not in stacks:
                        error("stackError/notFound: You're trying to use a stack-based command on a stack that doesn't even exist...?")
                    match rParam:
                        case "s": # swapius
                            stacks[lParam][-2], stacks[lParam][-1] = stacks[lParam][-1], stacks[lParam][-2]
                        case "q": # itemius deletius
                            del stacks[lParam][-1]
                        case "d": # duplicatius topius itemius
                            stacks[lParam].append(stacks[lParam][-1])
                        case "r": # reversius stackius
                            stacks[lParam].reverse()
                        case _:
                            error("parameterError/invalid: What do you expect me to do with the random-ass sub-command you chose?")
                    
                    cmdIndex += 2
                    continue

                case ">": # << stack A << | >> stack B >>
                    if lParam not in stacks or rParam not in stacks:
                        error("stackError/notFound: Either one or both stacks don't exist. Idk, try specifying one that does exist or creating one?")

                    stacks[rParam].append(stacks[lParam].pop(-1))

                    cmdIndex += 2
                    cmd = ""
                    continue


                # I/O
                
                case "i": # << stack << | >> mode >>
                    if lParam not in stacks:
                        error("stackError/notFound: Uhh, I can take input, but what am I supposed to do with it?")

                    match rParam: # checkius subius commandius
                        case "c": # characterius
                            temp = input("Enter one character as input (it will only take one character anyway):\n> ")[0]
                            stacks[lParam] = ord(temp)
                        case "i": # numberius
                            try:
                                temp = float(input("Enter a number as input (decimals will be truncated):\n> "))
                            except ValueError:
                                error("valueError/wrongType: Dude you needed a number and you typed a non-number. I don't even have anything more to say. READ THE DAMN INSTRUCTIONS FOR ONCE.")
                            
                            stacks[lParam].append(trunc(temp))

                    cmdIndex += 2
                    continue

                case "o": # << stack << | >> mode >>
                    if lParam not in stacks:
                        error("stackError/notFound: Ok, so you know how outputting pops the value? Yeah I didn't learn how to pop from nothingness.")
                    
                    match rParam:
                        case "c": # characterius
                            try:
                                temp = stacks[lParam].pop(-1)
                            except IndexError:
                                error("stackError/notEnoughItems: Mmmm, outputting nothing.")

                            output += chr(temp)

                        case "i":
                            try:
                                temp = stacks[lParam].pop(-1)
                            except IndexError:
                                error("stackError/notEnoughItems: I get that you want to show a number, but, uhh, what number?")

                            output += str(temp)

                    cmdIndex += 2
                    continue


                # ARITHMETIC / LOGIC

                case "a": # << stack << | >> sub command >>
                    if lParam not in stacks:
                        error("stackError/notFound: Good luck taking two numbers from nothing. Try it for yourself.")
                
                    if rParam in "+-*/%":
                        try:
                            tempX, tempY = stacks[lParam].pop(-1), stacks[lParam].pop(-1)
                        except IndexError:
                            error("stackError/notEnoughItems: You need two values to do your thing. You don't have enough. Please add more. I'm not doing it for you. Plus, I don't even know what you want to add.")
                        try:
                            exec(f"stacks[lParam].append(tempY{rParam}tempX)")
                        except ZeroDivisionError:
                            error("valueError/divisionByZero: What is x divided by 0 again?")
                    else:
                        error("parameterError/invalid: It's either +, -, *, /, or %. You got that?")

                    cmdIndex += 2
                    continue

                case "l": # << stack << | >> sub command >>
                    if lParam not in stacks:
                        error("stackError/notFound: Doing logic on nothing. Genius.")
                
                    if rParam in ">=<":
                        try:
                            tempX, tempY = stacks[lParam].pop(-1), stacks[lParam].pop(-1)
                        except IndexError:
                            error("stackError/notEnoughItems: How in the world do you compare less than two things? From what I'm seeing it's like comparing 5 to  .")
                        
                        exec(f"temp = tempY{rParam}tempX")
                        stacks[lParam].append(1 if temp else 0)
                    else:
                        error("parameterError/invalid: Be honest here. Do I need more comparisons? You're lucky you even have a less than operator. I could just use greater than and you'd have to invert it yourself.")

                    cmdIndex += 2
                    continue

                case "!": # >> stack >> [bitwise not]
                    if rParam not in stacks:
                        error("stackError/notFound: Bruh.")
                    
                    try:
                        temp = stacks[rParam].pop(-1)
                    except IndexError:
                        error("stackError/notEnoughItems: What am I supposed to inverse?")

                    stacks[rParam].append(1 if temp == 0 else 0)

                    cmdIndex += 2
                    continue
                
                case "R": # >> stack >> [jump to line if other value is non-zero]
                    if rParam not in stacks:
                        error("stackError/notFound: Dude you want me to give you a random number and you don't even give me a range?")
                    
                    try:
                        tempX, tempY = stacks[rParam].pop(-1), stacks[rParam].pop(-1)
                    except IndexError:
                        error("stackError/notEnoughItems: Please give me a proper range.")

                    stacks[rParam].append(randint(tempY, tempX))

                    break


                # CONDITIONAL BRANCHING (the cool part)

                case "u": # >> stack >> [jump to line no matter what]
                    if rParam not in stacks:
                        error("stackError/notFound: Just read the error.")
                    
                    try:
                        temp = stacks[rParam].pop(-1)
                    except IndexError:
                        error("stackError/notEnoughItems: So, you need a number, aka the line, to jump to. If you don't have one, where am I supposed to go?")

                    if temp >= line:
                        line = temp - 2
                        cmdIndex = 0
                    else:
                        line += 1
                        cmdIndex = 0

                    break

                case "b": # >> stack >> [jump to line if other value is non-zero]
                    if rParam not in stacks:
                        error("stackError/notFound: Just read the error.")
                    
                    try:
                        tempX, tempY = stacks[rParam].pop(-1), stacks[rParam].pop(-1)
                    except IndexError:
                        error("stackError/notEnoughItems: You need a line number to jump to and another number as whether to do it or not.")

                    if tempX != 0:
                        line = tempY - 2 # Subtract 2 because the line number in the code is 0-indexed
                    else:
                        line += 1
                        cmdIndex = 0

                    break

                # TODO: try to add commenting?


                case _: # none of the above
                    pass


            cmdIndex += 1
        
        cmdIndex = 0
        line += 1

    except IndexError: # hits end of file
        break

# print out stuff at the end
print(f"\n\nEnd of execution results:\n\n  Stacks: {stacks}\n\n  Output: {output}\n")
