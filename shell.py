# This is the shell, to run any spindle program:
# 1. Ensure you have spindle.py in the same directory
# 2. Run shell.py
# 3. Type "RUN(" + [the file you want to run with the .spdl extension] + ")"
#       - Example: RUN("HELLO_spindle.spdl")
# 4. Press enter, and if everything works correctly, you should get an output!

import spindle


print("Welcome! \nYou now programming with spindle ✨ \n")
while True:
    text = input('✨ | Spindle > ')
    if text.strip() == "":
        continue
    result = spindle.run('<stdin>', text)
    print("\n")
    print(str(repr(result)).replace("None",""))
    
    
