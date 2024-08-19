import sparkle
while True:
  text = input("Sparkle > ")
  result, error = sparkle.run('<placeholder>' , text)
  if error:
    print(error.as_string())
  else:
    print(result)
