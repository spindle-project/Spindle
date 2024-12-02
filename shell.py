# This is the shell, to run any sparkle program:
# 1. Ensure you have sparkle.py in the same directory
# 2. Run shell.py
# 3. Type "RUN(" + [the file you want to run with the .spkl extension] + ")"
#       - Example: RUN("HELLO_SPARKLE.spkl")
# 4. Press enter, and if everything works correctly, you should get an output!

import sparkle
token_list = []
program_text = ""
proc_flag = False

def semi_parse_string(string):
    """Divides the given string into a list of strings based on PROCEDURE keywords and curly brace nesting.

    Args:
        string: The input string to be divided.

    Returns:
        A list of strings, where each string is a separate procedure or code block.
    """

    result = []
    current_block = []
    brace_depth = 0

    for line in string.splitlines():
        if line.startswith("PROCEDURE"):
            if current_block:
                result.append("".join(current_block))
            current_block = [line + " \n "]
            brace_depth = 0
        else:
            current_block.append(line + " \n ")
            if "{" in line:
                brace_depth += line.count("{")
            if "}" in line:
                brace_depth -= line.count("}")
            if brace_depth == -1:
                result.append("".join(current_block))
                current_block = []
    if current_block != []:
        result.append("".join(current_block))


    return result

print("Welcome! \nYou now programming with Sparkle ✨ \n")
while True:
    text = input('✨ | Sparkle > ')
    if text.strip() == "":
      continue

    # Create tokens just for the sake of figuring out wheter we're dealing with a RUN command or a procedure
    tokens = sparkle.generate_tokens('<stdin>', text)
    if str(tokens[0]) == "IDENTIFIER:RUN": # Test wheter the current script has a RUN FILE function
        text = sparkle.get_file_text(str(tokens[2]).split(":")[1])
    # Test wheater or not code contains a function.
    if "PROCEDURE" in text: # There's a procedure!!! Use sublists
      proc_flag = True
      program_text = semi_parse_string(text)
    else :
      program_text = text
      result,error = sparkle.run('<stdin>', text)
      if error: 
          print(error.as_string())
      else:
          print(str(repr(result)).replace("-1.010203040506071",""))

    if proc_flag:
      proc_flag = False
      for i in range(len(program_text)): # Run each part of the text seperatly
        if program_text[i].strip() == "":
          continue
        result,error = sparkle.run('<stdin>', program_text[i])
        if error: 
            print(error.as_string())
            break
        else:
            print(str(repr(result)).replace("-1.010203040506071",""))  
    
