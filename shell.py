# This is the shell, to run any sparkle program:
# 1. Ensure you have sparkle.py in the same directory
# 2. Run shell.py
# 3. Type "RUN(" + [the file you want to run with the .spkl extension] + ")"
#       - Example: RUN("HELLO_SPARKLE.spkl")
# 4. Press enter, and if everything works correctly, you should get an output!

import sparkle


print("Welcome! \nYou now programming with Sparkle ✨ \n")
while True:
    text = input('✨ | Sparkle > ')
    if text.strip() == "":
        continue
    result = sparkle.run('<stdin>', text)
    print("\n"+str(repr(result)).replace("None","")+"\n")
     
    
