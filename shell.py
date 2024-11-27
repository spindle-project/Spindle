import sparkle
print("Welcome! \nYou now programming with Sparkle ✨ \n")
while True:
    text = input('✨ | Sparkle > ')
    if text.strip() == "":
        continue
    result,error = sparkle.run('<stdin>', text)
    if error: 
        print(error.as_string())
    else:
        print("\n"+str(repr(result))+"\n")
 