#  Welcome to ✨ Sparkle ✨

**The language used in the AP CSP Exam, now actually a programming language!**

## **Programming Guide**

## ✖️ Variables:
Varibles can be assigned a value using "<--" OR "<-"
For example, the following code sets a to 10 and then to 13 (a's value plus 3). 
```
a <- 10
a <-- 13
```
 Varibles can be assigned to other varibles!
```
b <-- a / 2
```
If you added this line to the lines above, it would set b to a's value divided by 2, resulting in 6.5

<details>
  <summary>How would you swap the values of two variables? </summary>
  
  ```m
a <-- 10
b <-- 10
c <--  a
a <-- b
b <-- c
```
  
</details>

## 💡 Logical Operators:
NOT: Negates the condition <br> 
AND: Returns TRUE if and only if BOTH conditions are TRUE <br>
OR: Returns TRUE if <i> at least one </i> of the conditions are true <br>

## 🆚 Comparison Operators:
<b>In this language: <br />
  0 is FALSE <br />
  1 is TRUE </b>

  The supported comparison operators are: 
  1. < &nbsp;&nbsp;   &nbsp;&nbsp; 4. \>= 
  2. <= &nbsp;&nbsp;  5. ==
  3. \> &nbsp;&nbsp; &nbsp;&nbsp;  6. !=

## ❔ If Statements:
If Statements can be defined with the keyword IF, and then the expression that must be true. The code that is to be ran when the the condition is met must be wrapred in brackets. If the condition for the IF statement is false, you can write an ELSE statement that will be ran instead
```
a <-- 5
IF a==5 {1} ELSE {0}
```
## 🔄 For Loops
For Loops are defined by the keyword REPEAT, followed by the number of times you want it to repeat, the keyword TIMES, and finally the code you want to be repeated
```
a <-- 5
REPEAT 10 TIMES {a <-- a + 1}
a
```
In the example above, a would now have the value of 15
## 🔁 While Loops
While loops are defined by the keywords REPEAT UNTIL, then the condition [surrounded by ()], and then the code you want repeated [surrounded by {}]
Like the code reads, the loop will run <i> until </i> the condition is true. You can think it as a while loop running while (NOT condition)
```
a <-- 10
REPEAT UNTIL (a > 30) { a <-- a + 4}
```
In the example above, a would now have the value of 34

## 🔁 Functions
Functions are defined by the keyword 'PROCEDURE', then the function name and or arguments [surrounded by ()], and then the code you want in the function body [surrounded by {}]
```
some_function <-- 0
PROCEDURE mystery(a) { a + 12}
some_function <-- mystery
some_function(12)
```
In the example above, line 4 would return 24

## 📖 Resources

 <b>The AP Computer Science Exam Reference Sheet can be found here:  *https://apcentral.collegeboard.org/media/pdf/ap-computer-science-principles-exam-reference-sheet.pdf*</b>

<b> Writen with the help of a tutorial by CodePulse, which can be found here: *https://youtu.be/Eythq9848Fg?si=yDuSPkEzG2y1X1cm*</b>
