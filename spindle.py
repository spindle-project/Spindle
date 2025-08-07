#######################################
def run_python_code(e):
    # Load and execute the code from my_module.py
    result = run('<INTERNAL>',text_input)
    if result == None:
        result = ""
    # Use the function from my_module.py
    display_res(result)


def display_res(text):
    print(text)


# IMPORTS 
# Spindle relys on these libaires to function
#os - Assess port to the os, allows the RUN("") command to fetch the name of the file the devloper wants to run

# As stated above, the function of the string and math imports are planned to be hardcoded in - so that they can be removed
#######################################
import os
#######################################
# CONSTANTS
# Put any values that you wish to stay the same globally here.
#######################################
PI = 3.141592653589793
DIGITS = '0123456789'
LOWERCASE_LETTERS = "abcdefghijklmnopqrstuvwxyz"
UPPERCASE_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LETTERS = UPPERCASE_LETTERS + LOWERCASE_LETTERS
LETTERS_DIGITS = LETTERS + DIGITS

#######################################
# Temporary varbles
# These varibles are not constants, but are global varibles Spindle needs to function
# Repositioning these to the approciate scope should happen sooner rather than later,
#######################################
REPEAT_STATEMENT_FIRST_CHAR = None
IN_REPEAT_LOOP = False
def CHANGE_IN_REPEAT_LOOP():
	global IN_REPEAT_LOOP
	IN_REPEAT_LOOP = not IN_REPEAT_LOOP
#######################################
# ERRORS
#######################################

# This function provides fancy error arrows when an error happens
''''
Example:
Runtime Error: 'karel' is not defined

karel 
^^^^
'''
def string_with_arrows(text, pos_start, pos_end):
    result = ''

    # Calculate indices
    idx_start = max(text.rfind('\n', 0, pos_start.idx), 0)
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0: idx_end = len(text)
    
    # Generate each line
    line_count = pos_end.ln - pos_start.ln + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[idx_start:idx_end]
        col_start = pos_start.col if i == 0 else 0
        col_end = pos_end.col if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + '\n'
        result += ' ' * col_start + '^' * (col_end - col_start)

        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0: idx_end = len(text)

    return result.replace('\t', '')


# This is the home of the Error class. When the programmer does something wrong, this will be called.
class Error:
    # Time to make a new error. 
	def __init__(self, pos_start, pos_end, error_name, details):
		self.pos_start = pos_start
		self.pos_end = pos_end
		self.error_name = error_name
		self.details = details
	# How the error looks like as a string. This is what is displayed to the end programmer.
	def as_string(self):
		result = "\n[*** Error! ***] \n"
		result += f' -- Summary:\n'
		result += f'  Type: {self.error_name} | Details: {self.details}'
		result += f'\n -- Location:\n'
		result += f'  File: {self.pos_start.fn} | Line: {self.pos_start.ln + 1} \n'
		result += '\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        
		return result
# Types of Errors
'''
IllegalCharError: You have a chacter where it's not supposed to be
ExpectedCharError: You are missing a chacter that needs to be there
InvalidSyntaxError: IllegalCharError, but on a syntax level. Usually the easiest to fix. 
RTError: The scarest error. Happens when Spindle physically cannot run the code, or if Spindle itself breaks
'''
class IllegalCharError(Error):
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Illegal Character', details)
class ExpectedCharError(Error):
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Expected Character', details)
class InvalidSyntaxError(Error):
	def __init__(self, pos_start, pos_end, details=''):
		super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class RTError(Error):
	def __init__(self, pos_start, pos_end, details, context):
		super().__init__(pos_start, pos_end, 'Runtime Error', details)
		self.context = context
  
  
 # This type of error  overrides the default error as_string() method
	def as_string(self):
		result  = self.generate_traceback()
		result += f'{self.error_name}: {self.details}'
		result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
		return result
 # Generate a nice looking traceback to help the programmer find the error
	def generate_traceback(self):
		result = ''
		pos = self.pos_start
		ctx = self.context
		traceback_num = 1
		while ctx:
			result = f'  {traceback_num}. File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
			pos = ctx.parent_entry_pos
			ctx = ctx.parent
			traceback_num += 1
		return result

#######################################
# POSITION
# This keeps track of where in the string Spindle is when it is running it. 
# Both at the text and token level. 
#######################################

class Position:
	def __init__(self, idx, ln, col, fn, ftxt):
		self.idx = idx
		self.ln = ln
		self.col = col
		self.fn = fn
		self.ftxt = ftxt
  
# Move to the next chacter or token
	def advance(self, current_char=None):
		self.idx += 1
		self.col += 1

		if current_char == '\n': # handle newlines differnely 
			self.ln += 1
			self.col = 0

		return self
# Make a copy of Spindle's current position 
	def copy(self):
		return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

#######################################
# TOKENS
# Text ran by Spindle is transformed into these before it is ran
#######################################

# DATA TYPES
TT_INT			= 'INT' # Whole numbers like 3, 4 or 5
TT_FLOAT    = 'FLOAT' # Numbers with a decimol point like: 3.14159
TT_STRING = 'STRING' # Text. In Spindle strings are surrounded by ". Ex "Hello!"

# EXPRESSSIONS
TT_PLUS     = 'PLUS' # Plus sign (+)
TT_MINUS    = 'MINUS' # Minus sign (-)
TT_MUL      = 'MUL' # Multiplication sign (*)
TT_DIV      = 'DIV' # Divison sign (/)
TT_POW			= 'POW' # Power sign (**). LEGACY, will be removed soon 


# COMPARASON OPERATORS
TT_EE = 'EE' # Equals sign (==)
TT_NE = 'NE' #  NOT Equals sign (!=)
TT_LT = 'LT' # Less than sign (<)
TT_GT = 'GT' # Greater than sign (>)
TT_LTE	= 'LTE' # Less than or equal sing (<=)
TT_GTE	= 'GTE' # Less than or equal sing (<=)

# CHARACTER LEVEL SYNTAX 
TT_LSQUARE = 'LSQUARE' # ([)
TT_RSQUARE = 'RSQUARE' # (])
TT_LBRACE = 'TT_LBRACE' # ({)
TT_RBRACE = 'TT_RBRACE' # (})
TT_LPAREN   = 'LPAREN' # Left Partenthesis "("
TT_RPAREN   = 'RPAREN' # Right Partenthesis ")"
TT_COMMA = 'COMMA' # Comma (,)
TT_EQ = 'EQ' # Equals sign (<--) OR (<-), but only the two dash one is tested. 
TT_NEWLINE = 'NEWLINE' # Newline (\n)


# IMPORTANT
TT_EOF			= 'EOF' # End of File. Automattically added to the end of the file. 
TT_IDENTIFIER = 'IDENTIFIER' # Identifer, used to denote varibles
TT_KEYWORD = 'KEYWORD' # Keyword, used to identifiy an important word in Spindle
KEYWORDS = [
    # COMPARASON. Imagine two values or expressions: a and b
    'AND', # True if a and b are True
	'OR', # True if either a is true or if b is true
	'NOT', # If a is true, retuns false. And vice-versa
	'IF', # IF statement
	'ELSE', # ELSE statement. Must be appended to an if statement
	'TIMES', # Used in a for loop
	'REPEAT', # Used in both for and while loops
	'TO', # LEGACY, has no use and will be removed soon
	'WHILE', # LEGACY. Remove this. 
	'PROCEDURE', # Used to denote functions
	'RETURN', # Return a value from a function
	'CONTINUE', # LEGACY - Maintainted, but only to be documented if collegeboard adds it
	'BREAK' # LEGACY - Maintainted, but only to be documented if collegeboard adds it
	]

# The Token class
class Token:
    # Make a new token
	def __init__(self, type_, value=None, pos_start=None, pos_end=None):
		self.type = type_
		self.value = value

		if pos_start:
			self.pos_start = pos_start.copy()
			self.pos_end = pos_start.copy()
			self.pos_end.advance()

		if pos_end:
			self.pos_end = pos_end
   
	# Checks if a token has a specific value
	def matches(self, type_,value):
		return self.type == type_ and self.value == value

	# String repersentation of a token
	def __repr__(self):
		if self.value: return f'{self.type}:{self.value}'
		return f'{self.type}'

#######################################
# LEXER
# Makes tokens!
#######################################

class Lexer:
	def __init__(self, fn, text):
		self.fn = fn
		self.text = text
		self.pos = Position(-1, 0, -1, fn, text)
		self.current_char = None
		self.advance()
	# Advance to the next character
	def advance(self):
		self.pos.advance(self.current_char)
		self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
  
	'''
 Handles the token making process. Checks every character in a string of text and assigns tokens to them
 	''' 
	def make_tokens(self):
		tokens = [] # <-- List of tokens
		while self.current_char != None:
			if self.current_char in ' \t':
				self.advance() # Igore
			elif self.current_char == "#":
				self.skip_comment() # This denotes a comment, ignore it and any letters after it until a newline
			elif self.current_char in";\n": # For ternimal use only, ";" may represent a newline
				tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
				self.advance()
			elif self.current_char in DIGITS: # Make a number!
				tokens.append(self.make_number())
				#varibles
			elif self.current_char == '"' or self.current_char == ".": #Make a string!
				tokens.append(self.make_string())
			# Strings must be surrounded by duouble quotes. 
			# IF is not the same as "IF"
			elif self.current_char in LETTERS: # serach for keywords. 
				#TEST for For loop
				if self.current_char == 'R': #<-- Feature update, make looking for for loops more precise 
					self.advance()
					#Test for RUN command, by checking the second letter. 
					'''
					For loops: REPEAT x TIMES
					RUN command: RUN("")
     				'''
					if self.current_char == 'U':
						self.advance()
						if self.current_char == 'N':
							self.advance()
						else:
							return [], InvalidSyntaxError( self.pos, self.pos, f"Expected RUN Command, got RU{self.current_char}")
						tokens.append(self.make_identifier("RUN FUNC BYPASS"))
						continue
					# Now that we know we have "RE", we need to insure that we don't have a RETURN statement
					elif self.current_char == 'E':
						self.advance()
						if self.current_char == 'P':
							char_list = ""
							for i in range(3):
								self.advance()
								char_list += self.current_char
							if char_list != "EAT":
								return [], InvalidSyntaxError( self.pos, self.pos, f"Expected 'REPEAT' got REP{self.current_char}")
    
							''' 
       						Now we know we have "REPEAT", but both of the "for" and "while" loops start with this, 
       						so we have to check for a while loop
							For loops: REPEAT x TIMES
							While Loops: REPEAT UNTIL (expr)
							'''
							self.advance()
							self.advance()
							if self.current_char == 'U': # We have a while loop because the next character is a "U"
								char_list = ""
								for i in range(4):
									self.advance()
									char_list += self.current_char
         
								if char_list != "NTIL":
									return [], InvalidSyntaxError( self.pos, self.pos, f"Expected 'UNTIL' got U{self.current_char}")
     
								self.advance()
								if self.current_char != " ":
									return [], ExpectedCharError( self.pos, self.pos, f"Expected ' ' got {self.current_char}")
								tokens.append(self.make_identifier("WHILE_LOOP_BYPASS"))
								tokens.append(Token(TT_KEYWORD, "NOT", self.pos, self.pos))
								continue
							# We do not have a while loop so we must have a for loop
							tokens.append(self.make_identifier("FOR_LOOP_BYPASS"))
							if self.make_identifier("FOR_LOOP_IDENITIFER_BYPASS") != None:
								tokens.append(self.make_identifier("FOR_LOOP_IDENITIFER_BYPASS"))	
							continue
						else:
							# We have a return statement
							char_list = ""
							for i in range(4):
								self.advance()
								char_list += self.current_char
							if char_list != "TURN":
								return [], InvalidSyntaxError( self.pos, self.pos, f"Expected 'RETURN' got RE{self.current_char}")
							tokens.append(Token(TT_KEYWORD, "RETURN", self.pos, self.pos))
							continue			
				else: # We do not have any loop or keyword. 
				# Append the identifier token like normal
					tokens.append(self.make_identifier())
					if self.current_char == '[':
						tokens.append(Token(TT_DIV, pos_start=self.pos))
						self.advance()
						while str(self.current_char) in DIGITS and not self.current_char == ']':
							tokens.append(self.make_number())
						if self.current_char == ']':
							self.advance()
						else:
							return [], ExpectedCharError( self.pos, self.pos, f"Expected ']' got {self.current_char}")

			# Check for comparason operators and operators			
			elif self.current_char == '<':
				self.advance()
				if self.current_char == '-':
					tokens.append(Token(TT_EQ, pos_start=self.pos))
					self.advance()
					if self.current_char == '-':
						self.advance()
				else:
					tokens.append(self.make_less_than())
			elif self.current_char == '>':
				tokens.append(self.make_greater_than())
			elif self.current_char == '{':
				tokens.append(Token(TT_LBRACE, pos_start=self.pos))
				self.advance()
			elif self.current_char == '}':
				tokens.append(Token(TT_RBRACE, pos_start=self.pos))
				self.advance()
				self.advance()
			elif self.current_char == '+':
				tokens.append(Token(TT_PLUS, pos_start=self.pos))
				self.advance()

			elif self.current_char == '=':
				self.advance()
				if self.current_char == '=':
					tokens.append(self.make_equals())
					self.advance()

				else: # Remember, (==) is different from (=). One exists and one does not. 
					return [], ExpectedCharError( self.pos, self.pos, "Expected '==', not '='")
			elif self.current_char == '-':
				tokens.append(Token(TT_MINUS, pos_start=self.pos))
				self.advance()
			elif self.current_char == '*':
				tokens.append(Token(TT_MUL, pos_start=self.pos))
				self.advance()
			elif self.current_char == '/':
				tokens.append(Token(TT_DIV, pos_start=self.pos))
				self.advance()
			elif self.current_char == '^':
				tokens.append(Token(TT_POW, pos_start=self.pos))
				self.advance()
			elif self.current_char == '(':
				tokens.append(Token(TT_LPAREN, pos_start=self.pos))
				self.advance()
			elif self.current_char == ')':
				tokens.append(Token(TT_RPAREN, pos_start=self.pos))
				self.advance()

			elif self.current_char == ']':
				tokens.append(Token(TT_RSQUARE, pos_start=self.pos))
				self.advance()
				if self.current_char == '[':
					tokens.append(Token(TT_DIV, pos_start=self.pos))
					self.advance()
					while str(self.current_char) in DIGITS and not self.current_char == ']':
						tokens.append(self.make_number())
						#self.advance()
					if self.current_char == ']':
						self.advance()
					else:
						return [], ExpectedCharError( self.pos, self.pos, f"Expected ']' got {self.current_char}")

			elif self.current_char == '[':
				tokens.append(Token(TT_LSQUARE, pos_start=self.pos))
				self.advance()
			elif self.current_char == '!':
				tok, error = self.make_not_equals()
				if error: return [], error
				else:
					tokens.append(tok)
			elif self.current_char == ',':
				tokens.append(Token(TT_COMMA, pos_start=self.pos))
				self.advance()
			else: # We do not know what chacter this is!
				pos_start = self.pos.copy()
				char = self.current_char
				self.advance()
				return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")
		# Append the End of file token and make sure to remove any that are "None"
		tokens.append(Token(TT_EOF, pos_start=self.pos))
		tokens  = [i for i in tokens if i is not None]
		return tokens, None

# The process for making a number
	def make_number(self):
		num_str = ''
		# This fixes for loops, please ignore the jankyness
		if IN_REPEAT_LOOP == True:
			num_str = '0'
			CHANGE_IN_REPEAT_LOOP()
		# Back to regular number making
		char_to_append = None
		dot_count = 0
		pos_start = self.pos.copy()
		# Add chacters to a number
		while self.current_char != None and self.current_char in DIGITS + '.':
			if self.current_char == '.':
				if dot_count == 1: break
				dot_count += 1
				num_str += '.'
			else:
				num_str += self.current_char
			self.advance()
		# Add the last digit
		if self.current_char != None and self.current_char in DIGITS + '.':
			num_str += self.current_char
			self.advance()
		# Return a INT or a FLOAT based on whether there's a "." or not
		if dot_count == 0:
			return Token(TT_INT, int(num_str), pos_start, self.pos)
		else:
			return Token(TT_FLOAT, float(num_str), pos_start, self.pos)
		
	# The process of making a string!
	def make_string(self):
		string = ""	
		pos_start = self.pos.copy()
		escape_character = False
		self.advance()

		escape_characters = {
			'n': '\n',
			't': '\t'
		}

		while self.current_char != None and (self.current_char != '"' or escape_character):
			if escape_character:
				string += escape_characters.get(self.current_char, self.current_char)
				escape_character = False 
			else:
				if self.current_char == '\\':
					escape_character = True
				else:
					string += self.current_char
			self.advance()	
		self.advance()
		return Token(TT_STRING, string, pos_start, self.pos)
	
	# The process of making a identfier!

	def make_identifier(self, bypass = None):
		try:
			pos_start = self.pos.copy()
		except:
			pos_start = 0
		# Bypasses are used when we need to dynamically insert tokens into the token list
		if bypass == "ELSE BYPASS":
			return Token(TT_KEYWORD, "ELSE", pos_start, self.pos)
		if bypass == "RUN FUNC BYPASS":
			return Token(TT_IDENTIFIER, "RUN", pos_start, self.pos)
		if bypass == "WHILE_LOOP_BYPASS":
			return Token(TT_KEYWORD, "WHILE", pos_start, self.pos)
		if bypass == "FOR_LOOP_BYPASS" or bypass == "FOR LOOP BYPASS":
			CHANGE_IN_REPEAT_LOOP()
			return Token(TT_KEYWORD, "REPEAT", pos_start, self.pos)
		if bypass == "FOR_LOOP_IDENITIFER_BYPASS":
			return Token(TT_IDENTIFIER, "n", pos_start, self.pos)
		# With bypasses out of the way, the rest of this function makes identifiers
		id_str = ''
		while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
			id_str += self.current_char
			self.advance()

		if id_str == "":
			return None #stop the functon! There are no letters to make an identifier with
		if id_str not in KEYWORDS: # Not in keywords so it must be a function or varible
			return Token(TT_IDENTIFIER, id_str, pos_start, self.pos)
		else: # Is a keyword
			return Token(TT_KEYWORD, id_str, pos_start, self.pos)

# Differientciate "==" from "!="
	def make_not_equals(self):
		pos_start = self.pos.copy()
		self.advance()

		if self.current_char == '=':
			self.advance()
			return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None

		self.advance()
		return None, ExpectedCharError(pos_start, self.pos, "Expected '!=' not just '!'")
	# Make a "=="
	def make_equals(self):
		pos_start = self.pos.copy()
		return Token(TT_EE,pos_start = pos_start, pos_end = self.pos)
	# Make a "<"
	def make_less_than(self):
		tok_type = TT_LT
		pos_start = self.pos.copy()

		if self.current_char == '=':
			self.advance()
			tok_type = TT_LTE

		return Token(tok_type, pos_start=pos_start, pos_end=self.pos)
# Make a ">"
	def make_greater_than(self):
		tok_type = TT_GT
		pos_start = self.pos.copy()
		self.advance()
		if self.current_char == '=':
			self.advance()
			tok_type = TT_GTE

		return Token(tok_type, pos_start=pos_start, pos_end=self.pos)
	# Skip the "#" and all letters up to a new line chacter. This skips comments.
	def skip_comment(self):
		self.advance()

		while self.current_char != '\n':
			self.advance()

		self.advance()
#######################################
# NODES
# The actual datatypes in Spindle, you should never have to touch this. 
#######################################

class NumberNode: # Handles numbers, and their repersentations
	def __init__(self, tok):
		self.tok = tok

		self.pos_start = self.tok.pos_start
		self.pos_end = self.tok.pos_end

	def __repr__(self):
		return f'{self.tok}'
	

class StringNode: # Handles strings, and their repersentations
	def __init__(self, tok):
		self.tok = tok

		self.pos_start = self.tok.pos_start
		self.pos_end = self.tok.pos_end

	def __repr__(self):
		return f'{self.tok}'
	
class ListNode: # Handles lists (arrays), and their repersentations
  def __init__(self, element_nodes, pos_start, pos_end):
    self.element_nodes = element_nodes

    self.pos_start = pos_start
    self.pos_end = pos_end

class VarAccessNode: # Allows Spindle to assess the value of a varible
	def __init__(self, var_name_tok):
		self.var_name_tok = var_name_tok
		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.var_name_tok.pos_end

class VarAssignNode: # Allows Spindle to set the value of a varible
	def __init__(self, var_name_tok, value_node ):
		self.var_name_tok = var_name_tok
		self.value_node = value_node

		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.value_node.pos_end

class BinOpNode: # Binary Operation node. DO NOT TOUCH!
	def __init__(self, left_node, op_tok, right_node):
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

		self.pos_start = self.left_node.pos_start
		self.pos_end = self.right_node.pos_end

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode: # Unary Operation Node, most notibily used in the !=
	def __init__(self, op_tok, node):
		self.op_tok = op_tok
		self.node = node

		self.pos_start = self.op_tok.pos_start
		self.pos_end = node.pos_end

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'
	
class IfNode: # If statements and Else cases
	def __init__(self, cases, else_case):
		self.cases = cases
		self.else_case = else_case

		self.pos_start = self.cases[0][0].pos_start
		self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end

class ForNode: # For loops in Spindle
	def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node, should_return_null):
		self.var_name_tok = var_name_tok
		self.start_value_node = start_value_node
		self.end_value_node = end_value_node
		self.step_value_node = step_value_node
		self.body_node = body_node
		self.should_return_null = should_return_null

		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.body_node.pos_end

class WhileNode: # While loops in Spindle
	def __init__(self, condition_node, body_node,should_return_null):
		self.condition_node = condition_node
		self.body_node = body_node
		self.should_return_null = should_return_null

		self.pos_start = self.condition_node.pos_start
		self.pos_end = self.body_node.pos_end

class FuncDefNode: # Defining functions in Spindle
	def __init__(self, var_name_tok, arg_name_toks, body_node,should_auto_return):
		self.var_name_tok = var_name_tok
		self.arg_name_toks =  arg_name_toks
		self.body_node = body_node
		self.should_auto_return = should_auto_return

		if self.var_name_tok:
			self.pos_start = self.var_name_tok.pos_start
		elif len(self.arg_name_toks) > 0:
			self.pos_start = self.arg_name_toks[0].pos_start
		else: 
			self.pos_start = self.body_node.pos_start
			
		self.pos_end = self.body_node.pos_end

class CallNode: # Calling functions in Spindle
	def __init__(self, node_to_call, arg_nodes):
		self.node_to_call = node_to_call
		self.arg_nodes = arg_nodes

		self.pos_start = self.node_to_call.pos_start

		if len(self.arg_nodes) > 0:
			self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
		else:
			self.pos_end = self.node_to_call.pos_end

class ReturnNode: # Retuning a value from a function in Spindle
	def __init__(self, node_to_return, pos_start, pos_end):
		self.node_to_return = node_to_return

		self.pos_start = pos_start
		self.pos_end = pos_end

# LEGACY - Maintained as collegeboard may add these
class ContinueNode: # Breaks out of that itteration of the loop
	def __init__(self, pos_start, pos_end):
		self.pos_start = pos_start
		self.pos_end = pos_end

class BreakNode: # Breaks out of the loop
	def __init__(self, pos_start, pos_end):
		self.pos_start = pos_start
		self.pos_end = pos_end


#######################################
# PARSE RESULT
# The result of Parsing!
#######################################

class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None
		self.last_registered_advance_count = 0
		self.advance_count = 0
		self.to_reverse_count = 0

	def register(self, res):
		self.last_registered_advance_count = res.advance_count
		self.advance_count += res.advance_count
		if res.error: self.error = res.error
		return res.node

	def register_advancement(self):
		self.advance_count += 1

	def try_register(self, res):
		if res.error:
			self.to_reverse_count = res.advance_count
			return None
		return self.register(res)

	def success(self, node): # Everything works!
		self.node = node
		return self

	def failure(self, error): # There was an error somewhere :(
		if not self.error or self.advance_count == 0:
			self.error = error
		return self

#######################################
# PARSER
# This is where the syntax for Spindle is defined. 
#######################################

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.tok_idx = -1
		self.advance()

	def advance(self): # Advance to the next token
		self.tok_idx += 1
		self.update_current_tok()
		return self.current_tok

	def reverse(self, amount=1): # Go back to the last token
		self.tok_idx -= amount
		self.update_current_tok()
		return self.current_tok

	def update_current_tok(self): # Update the current Token
		if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
			self.current_tok = self.tokens[self.tok_idx]
	
	def peek(self, amount): # Take a little look at the token *amount* away
		return self.tokens[self.tok_idx+amount]

	def parse(self): # Time to figure out that the tokens mean
		res = self.statements()
		# Ignore TT_EOF, TT_KEYWORD, TT_IDENTIFIER,TT_EQ,TT_RBRACE. These should not cause errors. Everything else should though!
		if not res.error and self.current_tok.type not in (TT_EOF, TT_KEYWORD, TT_IDENTIFIER,TT_EQ,TT_RBRACE):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '+', '-', '*', '/', ,'[', '^', '==', '!=', '<', '>', <=', '>=', 'AND' or 'OR'"
			))
		return res
	
# A statement is an expression
	def statement(self):
		res = ParseResult()
		pos_start = self.current_tok.pos_start.copy()

		if self.current_tok.matches(TT_KEYWORD, 'RETURN'):
			res.register_advancement()
			self.advance()

			expr = res.try_register(self.expr())
			if not expr:
				self.reverse(res.to_reverse_count)
			return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))
			
		if self.current_tok.matches(TT_KEYWORD, 'CONTINUE'):
			res.register_advancement()
			self.advance()
			return res.success(ContinueNode(pos_start, self.current_tok.pos_start.copy()))
		
		if self.current_tok.matches(TT_KEYWORD, 'BREAK'):
			res.register_advancement()
			self.advance()
			return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))
		expr = res.register(self.expr())
		if res.error:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected 'RETURN', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[' or 'NOT'"
			))
		return res.success(expr)
	# Statements is more than one statement
	def statements(self):
		res = ParseResult()
		statements = []
		pos_start = self.current_tok.pos_start.copy()

		while self.current_tok.type == TT_NEWLINE:
			res.register_advancement()
			self.advance()

		statement = res.register(self.statement())
		if res.error: return res
		statements.append(statement)

		more_statements = True

		while True:
			newline_count = 0
			while self.current_tok.type == TT_NEWLINE:
				res.register_advancement()
				self.advance()
				newline_count += 1
			if newline_count == 0:
				more_statements = False
			
			if not more_statements: break
			statement = res.try_register(self.statement())
			if not statement:
				self.reverse(res.to_reverse_count)
				more_statements = False
				continue
			statements.append(statement)

		return res.success(ListNode(
		statements,
		pos_start,
		self.current_tok.pos_end.copy()
		))

	


	def if_expr(self): # Creates an if node
		res = ParseResult()
		all_cases = res.register(self.if_expr_cases('IF'))
		if res.error: return res
		cases, else_case = all_cases
		return res.success(IfNode(cases, else_case))

	def if_expr_c(self): # Handles "ELSE" cases
		res = ParseResult()
		else_case = None
		while self.current_tok.type == TT_NEWLINE:
			res.register_advancement()
			self.advance()

		if self.current_tok.matches(TT_KEYWORD, 'ELSE'):
			res.register_advancement()
			self.advance()

			while self.current_tok.type == TT_NEWLINE:
				res.register_advancement()
				self.advance()

			if not self.current_tok.type == TT_LBRACE:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected '{'"
				))

			res.register_advancement()
			self.advance()

			while self.current_tok.type == TT_NEWLINE:
				res.register_advancement()
				self.advance()

			statements = res.register(self.statements())
			if res.error: return res
			else_case = (statements, True)

			while self.current_tok.type == TT_NEWLINE:
				res.register_advancement()
				self.advance()

			if not self.current_tok.type == TT_RBRACE:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected '}'"
				))

			res.register_advancement()
			self.advance()

		return res.success(else_case)

	def if_expr_b_or_c(self): # Figures out whether to handle this as an IF or ELSE case
		res = ParseResult()
		else_case = None
		while self.current_tok.type == TT_NEWLINE:
			res.register_advancement()
			self.advance()
		if self.current_tok.matches(TT_KEYWORD, "ELSE"):
			else_case = res.register(self.if_expr_c())
			if res.error: return res
		return res.success(else_case)
	

	def if_expr_cases(self, case_keyword): # Handle the code inside IF and ELSE statements
		res = ParseResult()
		cases = []
		else_case = None
		if not self.current_tok.matches(TT_KEYWORD, case_keyword):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected '{case_keyword}'"
			))
		res.register_advancement()
		self.advance()
		if self.current_tok.type == TT_LPAREN:
			res.register_advancement()
			self.advance()
		condition = res.register(self.statement())
		if res.error: return res
		while self.current_tok.type == TT_NEWLINE:
					res.register_advancement()
					self.advance()
		
		if not self.current_tok.type  == TT_RPAREN: #NOTE: in(TT_LBRACE , TT_RPAREN)
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected ')'"
			))
		res.register_advancement()
		self.advance()
		if not self.current_tok.type == TT_LBRACE:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '{'"
			))
		res.register_advancement()
		self.advance()
		if self.current_tok.type == TT_NEWLINE:
			while self.current_tok.type == TT_NEWLINE:
				res.register_advancement()
				self.advance()

			statements = res.register(self.statements())
			if res.error: return res
			cases.append((condition, statements, True))
			while self.current_tok.type == TT_NEWLINE:
				res.register_advancement()
				self.advance()
			if self.current_tok.type == TT_RBRACE:
				res.register_advancement()
				self.advance()
				else_case = res.register(self.if_expr_b_or_c())
				if res.error: return res
			else:
				else_case = res.register(self.if_expr_b_or_c())
				if res.error: return res
				while self.current_tok.type == TT_NEWLINE:
					res.register_advancement()
					self.advance()
				if self.current_tok.type == TT_RBRACE:
					res.register_advancement()
					self.advance()
		else:
			expr = res.register(self.statements())
			if res.error: return res
			cases.append((condition, expr, True))

			else_case = res.register(self.if_expr_b_or_c())
			if res.error: return res

		return res.success((cases, else_case))

	def for_expr(self): # Handle for loops
		res = ParseResult()

		if not self.current_tok.matches(TT_KEYWORD, 'REPEAT'):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'REPEAT'"
			))

		res.register_advancement()
		self.advance()

		if self.current_tok.type != TT_IDENTIFIER:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected identifier 122"
			))

		var_name = self.current_tok

		
		res.register_advancement()
		self.advance()

		start_value = 0
		if res.error: return res
		a = res.register(self.expr())
		end_value = a
		if res.error: return res
		step_value = None
		if not self.current_tok.matches(TT_KEYWORD, 'TIMES'):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Your REPEAT or REPEAT UNTIL loop has the wrong syntax. Please deouble check that everything is spelled correctly."
			))

		res.register_advancement()
		self.advance()
		
		if not self.current_tok.type == TT_LBRACE:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '{'"
			))
		else:
			res.register_advancement()
			self.advance()
		
		if self.current_tok.type == TT_NEWLINE:
			res.register_advancement()
			self.advance()

			body = res.register(self.statements())
			if res.error: return res

			if not self.current_tok.type == TT_RBRACE:
				return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '}'"
				))

			res.register_advancement()
			self.advance()

			return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))

		body = res.register(self.statement())
		if res.error: return res

		if not self.current_tok.type == TT_RBRACE:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '}'"
			))
		else:
			res.register_advancement()
			self.advance()

		return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))

	def while_expr(self):
		res = ParseResult()

		if not self.current_tok.matches(TT_KEYWORD, 'WHILE'):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'WHILE'"
			))

		res.register_advancement()
		self.advance()
		condition = res.register(self.expr())
		if res.error: return res

		res.register_advancement()
		self.advance()

		if self.current_tok.type == TT_NEWLINE:
			res.register_advancement()
			self.advance()

			body = res.register(self.statements())
			if res.error: return res

			if not self.current_tok.type == TT_RBRACE:
				return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '}'"
				))

			res.register_advancement()
			self.advance()

			return res.success(WhileNode(condition, body, True))
    
		body = res.register(self.statement())
		if res.error: return res

		return res.success(WhileNode(condition, body, False))

	###################################
 # Call functions in Spindle
	def call(self):
		res = ParseResult()

		if self.current_tok.type == TT_RBRACE:
			return res.success(Number.null)
		atom = res.register(self.atom())
		if res.error: return res
		if self.current_tok.type == TT_LPAREN:
			res.register_advancement()
			self.advance()
			arg_nodes = []

			if self.current_tok.type == TT_RPAREN:
				res.register_advancement()
				self.advance()
			else:
				arg_nodes.append(res.register(self.expr()))
				if res.error:
					return res.failure(InvalidSyntaxError(
						self.current_tok.pos_start, self.current_tok.pos_end,
						"Expected ')', '[', 'VARIBLE IDENTIFIFER', 'IF', 'REPEAT', 'REPEAT UNTIL', 'PROCEDURE', int, float, identifier, '+', '-', '(' or 'NOT'"
					))

				while self.current_tok.type == TT_COMMA:
					res.register_advancement()
					self.advance()

					arg_nodes.append(res.register(self.expr()))
					if res.error: return res
				if self.current_tok.type != TT_RPAREN:
					return res.failure(InvalidSyntaxError(
						self.current_tok.pos_start, self.current_tok.pos_end,
						f"Expected ',' or ')'"
					))

				res.register_advancement()
				self.advance()
			return res.success(CallNode(atom, arg_nodes))
		return res.success(atom)

# Do things with numbers, while handling REPEAT, WHILE, and PROCEDURE
	def atom(self):
		res = ParseResult()
		tok = self.current_tok
		if tok.type in (TT_INT, TT_FLOAT):
			res.register_advancement()
			self.advance()
			return res.success(NumberNode(tok))
		
		if tok.type == TT_STRING:
			res.register_advancement()
			self.advance()
			return res.success(StringNode(tok))
		
		elif tok.matches(TT_KEYWORD, 'IF'):
					if_expr = res.register(self.if_expr())
					if res.error: return res
					return res.success(if_expr)
		
		elif tok.matches(TT_KEYWORD, 'REPEAT'):
			for_expr = res.register(self.for_expr())
			if res.error: return res
			return res.success(for_expr)

		elif tok.matches(TT_KEYWORD, 'WHILE'):
			while_expr = res.register(self.while_expr())
			if res.error: return res
			return res.success(while_expr)
		
		elif tok.matches(TT_KEYWORD, 'PROCEDURE'):
			func_def = res.register(self.func_def())
			if res.error: return res
			return res.success(func_def)
		
		elif tok.type == TT_IDENTIFIER:
			res.register_advancement()
			self.advance()
			return res.success(VarAccessNode(tok))

		elif tok.type == TT_LPAREN:
			res.register_advancement()
			self.advance()
			expr = res.register(self.expr())
			if res.error: return res
			if self.current_tok.type == TT_RPAREN:
				res.register_advancement()
				self.advance()
				return res.success(expr)
			
		elif tok.type == TT_LSQUARE:
			list_expr = res.register(self.list_expr())
			if res.error: return res
			return res.success(list_expr)

		else:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected ')'"
			))

			
		return res.failure(InvalidSyntaxError(
			tok.pos_start, tok.pos_end,
			"Expected int, float, identifier, '+', '-', '(', 'IF','REPEAT UNTIL', 'REPEAT', 'PROCEDURE'"
		))

	def list_expr(self): # Handle lists
		res = ParseResult()
		element_nodes = []
		pos_start = self.current_tok.pos_start.copy()

		if self.current_tok.type != TT_LSQUARE:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected '['"
			))

		res.register_advancement()
		self.advance()

		if self.current_tok.type == TT_RSQUARE:
			pass # Do nothing

		else:
			element_nodes.append(res.register(self.expr()))
			if res.error:
				return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected ']', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[' or 'NOT'"
				))

		while self.current_tok.type == TT_COMMA:
			res.register_advancement()
			self.advance()

			element_nodes.append(res.register(self.expr()))
			if res.error: return res

		if self.current_tok.type != TT_RSQUARE:
			return res.failure(InvalidSyntaxError(
			self.current_tok.pos_start, self.current_tok.pos_end,
			f"Expected ',' or ']' Got {str(self.current_tok)}"
			))

		res.register_advancement()
		self.advance()

		return res.success(ListNode(
		element_nodes,
		pos_start,
		self.current_tok.pos_end.copy()
		))
	def power(self): # Power Opperator. LEGACY
		return self.bin_op(self.call, (TT_POW, ), self.factor)

	def factor(self): # Transforms numbers into positive and negitive counterparts
		res = ParseResult()
		tok = self.current_tok

		if tok.type in (TT_PLUS, TT_MINUS):
			res.register_advancement()
			self.advance()
			factor = res.register(self.factor())
			if res.error: return res
			return res.success(UnaryOpNode(tok, factor))

		return self.power()

	def term(self): # Handle number expressiobs with * or /
		return self.bin_op(self.factor, (TT_MUL, TT_DIV))

	def arith_expr(self): # Handle number expressiobs with + or -
		return self.bin_op(self.term, (TT_PLUS, TT_MINUS))
	
	def comp_expr(self): # Combines expressions
		res = ParseResult()

		if self.current_tok.matches(TT_KEYWORD, 'NOT'):
			op_tok = self.current_tok
			res.register_advancement()
			self.advance()

			node = res.register(self.comp_expr())
			if res.error: return res
			return res.success(UnaryOpNode(op_tok, node))
		
		node = res.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))
		
		if res.error:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected int, float, identifier, '+', '-', '(', '[',  or 'NOT'"
			))

		return res.success(node)
	
	def expr(self): # Expressions! Includes assigning anything to a varible
		res = ParseResult()

		if self.current_tok.type == TT_IDENTIFIER and self.peek(1).type  in TT_EQ :
			# Assigning a value to a varible
			if self.peek(1).type not in  (TT_IDENTIFIER ,TT_EQ):
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected '<-' or '<--'"
				))
			var_name = self.current_tok
			self.advance()	
			self.advance()
			expr = res.register(self.expr())
			if res.error: return res
			return res.success(VarAssignNode(var_name, expr))
		if self.current_tok.type == TT_LBRACE: # Fix for for loops. Skip past the {
			self.advance()
		node =  res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, 'AND'),(TT_KEYWORD, 'OR'))))
		if res.error: 
			return res.failure(InvalidSyntaxError(
			self.current_tok.pos_start, self.current_tok.pos_end,
			"Expected 'VARIBLE IDENTIFIER', 'IF', 'REPEAT UNTIL', 'REPEAT', 'PROCEDURE', int, float, identifier, '+', '-', '[', or '(. \n Did you wrap an assigned varible in parenthesis?'"
		))
		return res.success(node)

	
	def func_def(self): # Define a function in Spindle. Syntax for it is here.
		res = ParseResult()

		if not self.current_tok.matches(TT_KEYWORD, 'PROCEDURE'):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'PROCEDURE'"
			))

		res.register_advancement()
		self.advance()

		if self.current_tok.type == TT_IDENTIFIER:
			var_name_tok = self.current_tok
			res.register_advancement()
			self.advance()
			if self.current_tok.type != TT_LPAREN:
				return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected '('"
				))
		else:
			var_name_tok = None
			if self.current_tok.type != TT_LPAREN:
				return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected identifier or '('"
				))
		
		res.register_advancement()
		self.advance()
		arg_name_toks = []

		if self.current_tok.type == TT_IDENTIFIER:
			arg_name_toks.append(self.current_tok)
			res.register_advancement()
			self.advance()
		
		while self.current_tok.type == TT_COMMA:
			res.register_advancement()
			self.advance()

			if self.current_tok.type != TT_IDENTIFIER:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					f"Expected identifier"
				))

			arg_name_toks.append(self.current_tok)
			res.register_advancement()
			self.advance()
		if self.current_tok.type != TT_RPAREN:
			return res.failure(InvalidSyntaxError(
			self.current_tok.pos_start, self.current_tok.pos_end,
			f"Expected ',' or ')'"
			))
		else:
			if self.current_tok.type != TT_RPAREN:
				return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected identifier or ')'"
				))

		res.register_advancement()
		self.advance()

		if self.current_tok.type == TT_LBRACE: 
			res.register_advancement()
			self.advance()

			body = res.register(self.statements())
			if res.error: return res

			return res.success(FuncDefNode(
				var_name_tok,
				arg_name_toks,
				body,
				True
			))
		
		if self.current_tok.type != TT_NEWLINE:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '{' or NEWLINE"
			))

		res.register_advancement()
		self.advance()

		body = res.register(self.statements())
		if res.error: return res

		res.register_advancement()
		self.advance()
		
		return res.success(FuncDefNode(
		var_name_tok,
		arg_name_toks,
		body, False
		))	

	###################################
	# Binary Operation between functions
	def bin_op(self, func_a, ops, func_b=None):
		if func_b == None:
			func_b = func_a
		
		res = ParseResult()
		left = res.register(func_a())
		if res.error: return res

		while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
			op_tok = self.current_tok
			res.register_advancement()
			self.advance()
			right = res.register(func_b())
			if res.error: return res
			left = BinOpNode(left, op_tok, right)

		return res.success(left)

#######################################
# RUNTIME RESULT
# Did the program Run?
#######################################

class RTResult:
	def __init__(self):
		self.reset()

	def reset(self):
		self.value = None
		self.error = None
		self.func_return_value = None
		self.loop_should_continue = False
		self.loop_should_break = False

	def register(self, res):
		self.error = res.error
		self.func_return_value = res.func_return_value
		self.loop_should_continue = res.loop_should_continue
		self.loop_should_break = res.loop_should_break
		return res.value

	def success(self, value):
		self.reset()
		self.value = value
		return self

	def success_return(self, value):
		self.reset()
		self.func_return_value = value
		return self
  
	def success_continue(self):
		self.reset()
		self.loop_should_continue = True
		return self

	def success_break(self):
		self.reset()
		self.loop_should_break = True
		return self

	def failure(self, error):
		self.reset()
		self.error = error
		return self
	
	def should_return(self):
    # Note: this will allow you to continue and break outside the current function - ending the program
		return (
		self.error or
		self.func_return_value or
		self.loop_should_continue or
		self.loop_should_break
		)

#######################################
# VALUES
# Handles numbers and math
#######################################
class Value:
	def __init__(self):
		self.set_pos()
		self.set_context()

	def set_pos(self, pos_start=None, pos_end=None):
		self.pos_start = pos_start
		self.pos_end = pos_end
		return self

	def set_context(self, context=None):
		self.context = context
		return self

# Update a number with arithmatic (+,-,*,/)... and **, but that's legacy
	def added_to(self, other):
		return None, self.illegal_operation(other)

	def subbed_by(self, other):
		return None, self.illegal_operation(other)

	def multed_by(self, other):
		return None, self.illegal_operation(other)

	def dived_by(self, other):
		return None, self.illegal_operation(other)

	def powed_by(self, other):
		return None, self.illegal_operation(other)

# Handle comparasons

	def get_comparison_eq(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_ne(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_lt(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_gt(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_lte(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_gte(self, other):
		return None, self.illegal_operation(other)

	def anded_by(self, other):
		return None, self.illegal_operation(other)

	def ored_by(self, other):
		return None, self.illegal_operation(other)

	def notted(self,other): #NOTE Added other to arguments. wasn't there in video
		return None, self.illegal_operation(other)

	def execute(self, args):
		return RTResult().failure(self.illegal_operation())

	def copy(self):
		raise Exception('No copy method defined')

	def is_true(self):
		return False

	def illegal_operation(self, other=None):
		if not other: other = self
		return RTError(
			self.pos_start, other.pos_end,
			'Illegal operation',
			self.context
		)

# The NUMBER class
class Number(Value):
	def __init__(self, value):
		super().__init__()
		self.value = value
# Arithmatic 
	def added_to(self, other):
		if isinstance(other, Number):
			return Number(self.value + other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def subbed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value - other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def multed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value * other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def dived_by(self, other):
		if isinstance(other, Number):
			if other.value == 0:
				return None, RTError(
					other.pos_start, other.pos_end,
					'Division by zero',
					self.context
				)

			return Number(self.value / other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def powed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value ** other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)
# Comparasons 
	def get_comparison_eq(self, other):
		if isinstance(other, Number):
			return Number(int(self.value == other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_ne(self, other):
		if isinstance(other, Number):
			return Number(int(self.value != other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_lt(self, other):
		if isinstance(other, Number):
			return Number(int(self.value < other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_gt(self, other):
		if isinstance(other, Number):
			return Number(int(self.value > other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_lte(self, other):
		if isinstance(other, Number):
			return Number(int(self.value <= other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_gte(self, other):
		if isinstance(other, Number):
			return Number(int(self.value >= other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)
# Expressions
	def anded_by(self, other):
		if isinstance(other, Number):
			return Number(int(self.value and other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def ored_by(self, other):
		if isinstance(other, Number):
			return Number(int(self.value or other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def notted(self):
		return Number(1 if self.value == 0 else 0).set_context(self.context), None

	def copy(self):
		copy = Number(self.value)
		copy.set_pos(self.pos_start, self.pos_end)
		copy.set_context(self.context)
		return copy

	def is_true(self):
		return self.value != 0
	
	def __repr__(self):
		return str(self.value)

	# BUILT IN NUMBERS. Null is a special constant. Hopefully no one will ever need it. 
Number.null = Number(-1.010203040506071) # Null constant - shell replaces with 'null'
Number.false = Number(0)
Number.true = Number(1)
Number.math_PI = PI


# Strings!
class String(Value):
	def __init__(self, value):
		super().__init__()
		self.value = value
# You can add strings to concatnate them
	def added_to(self, other):
		if isinstance(other, String):
			return String(self.value + other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)
# Multiply strings by a number works just like python.
	def multed_by(self, other):
		if isinstance(other, Number):
			return String(self.value * other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)
# Strings are true if they are not empty 
	def is_true(self):
		return len(self.value) > 0

	def copy(self):
		copy = String(self.value)
		copy.set_pos(self.pos_start, self.pos_end)
		copy.set_context(self.context)
		return copy

	def __str__(self):
		return self.value

	def __repr__(self):
		return f'"{self.value}"'

# Lists (arrays)
class List(Value):
  def __init__(self, elements):
    super().__init__()
    self.elements = elements

# Add an element into a list
  def added_to(self, other):
    new_list = self.copy()
    new_list.elements.append(other)
    return new_list, None
# Get rid of an element of a list
  def subbed_by(self, other):
    if isinstance(other, Number):
      new_list = self.copy()
      try:
        new_list.elements.pop(other.value-1)
        return new_list, None
      except:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Element at this index could not be removed from list because index is out of bounds',
          self.context
        )
    else:
      return None, Value.illegal_operation(self, other)

  def multed_by(self, other):
    if isinstance(other, List):
      new_list = self.copy()
      new_list.elements.extend(other.elements)
      return new_list, None
    else:
      return None, Value.illegal_operation(self, other)
# Diving a list to get an element of it. Do not think of [listelements]/5 is something. Instead think of [listelements][list index]
  def dived_by(self, other):
    if isinstance(other, Number):
      try:
        return self.elements[other.value-1], None
      except:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Element at this index could not be retrieved from list because index is out of bounds',
          self.context
        )
    else:
      return None, Value.illegal_operation(self, other)
  
  def copy(self): # Copy a list
    copy = List(self.elements)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def __repr__(self): # String repersentation of a list
    return ", ".join([str(x) for x in self.elements])
  def __str__(self):
    return f'[{", ".join([str(x) for x in self.elements])}]'
	
 
# The base function class. programmer and built in functions draw from this class
class BaseFunction(Value):
	def __init__(self,name):
		super().__init__()
		self.name = name or "<anonymous>"


	def generate_new_context(self):
		new_context = Context(self.name, self.context, self.pos_start)
		new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
		return new_context
	
	def check_args(self, arg_names, args):
		res = RTResult()
		if len(args) > len(arg_names):
			return res.failure(RTError(
				self.pos_start, self.pos_end,
				f"{len(args) - len(arg_names)} too many args passed into '{self.name}'",
				self.context
			))
		
		if len(args) < len(arg_names):
			return res.failure(RTError(
				self.pos_start, self.pos_end,
				f"{len(arg_names) - len(args)} too few args passed into '{self.name}'",
				self.context
			))
		return res.success(None)
	
	
	def populate_args(self, arg_names, args, exec_ctx):
		for i in range(len(args)):
			arg_name = arg_names[i]
			arg_value = args[i]
			arg_value.set_context(exec_ctx)
			exec_ctx.symbol_table.set(arg_name, arg_value)
	
	def check_and_populate_args(self, arg_names, args, exec_ctx):
		res= RTResult()
		res.register(self.check_args(arg_names, args))
		if res.should_return(): return res
		self.populate_args(arg_names, args, exec_ctx)
		return res.success(None)

# Handle functions!
class Function(BaseFunction):
	def __init__(self, name, body_node, arg_names, should_auto_return):
		super().__init__(name)
		self.body_node = body_node
		self.arg_names = arg_names
		self.should_auto_return = should_auto_return

	def execute(self, args):
		res = RTResult()
		interpreter = Interpreter()
		exec_ctx = self.generate_new_context()
		exec_ctx.symbol_table = SymbolTable(exec_ctx.parent.symbol_table)

		res.register(self.check_and_populate_args(self.arg_names,args,exec_ctx))
		if res.should_return(): return res

		value = res.register(interpreter.visit(self.body_node, exec_ctx))
		if res.should_return() and res.func_return_value == None: return res

		ret_value = (value if self.should_auto_return else None) or res.func_return_value or Number.null
		return res.success(ret_value)

	def copy(self):
		copy = Function(self.name, self.body_node, self.arg_names,self.should_auto_return)
		copy.set_context(self.context)
		copy.set_pos(self.pos_start, self.pos_end)
		return copy

	def __repr__(self):
		return f"<PROCEDURE {self.name}>"
	
 # Handle functions built into the language
class BuiltInFunction(BaseFunction):
	def __init__(self, name):
		super().__init__(name)

	def execute(self,args):
		res = RTResult()
		exec_ctx = self.generate_new_context()

		method_name = f'execute_{self.name}'
		method = getattr(self,method_name,self.no_visit_method)
		res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
		if res.should_return(): return res

		return_value = res.register(method(exec_ctx))
		if res.should_return(): return res
		return res.success(return_value)
	  
	def no_visit_method(self, node, context):
		raise Exception(f'No execute_{self.name} method defined')

	def copy(self):
		copy = BuiltInFunction(self.name)
		copy.set_context(self.context)
		copy.set_pos(self.pos_start, self.pos_end)
		return copy

	def __repr__(self):
		return f"<built-in function {self.name}>"
	
#######################################
# Built in Functions List
#######################################	



	def execute_display(self, exec_ctx): # Displays a value to the console
		display_res(str(exec_ctx.symbol_table.get('value')))
		return RTResult().success(Number.null)
	execute_display.arg_names = ["value"]

	# Input() function, takes input.
	def execute_input(self, exec_ctx):
		text = input()
		# Test for a number!
		try: # we have one!
			val = int(text)
			return RTResult().success(Number(val))
		except ValueError: # Not one
			return RTResult().success(String(text))
	execute_input.arg_names = []

 # Clear command. 
	def execute_clear(self, exec_ctx): # Clears ternimal screen
		os.system('cls' if os.name == 'nt' else 'cls') 
		return RTResult().success(Number.null)
	execute_clear.arg_names = []
 
 # is the parmeter a specific data type? Functions
	def execute_is_number(self, exec_ctx): #
		is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
		return RTResult().success(Number.true if is_number else Number.false)
	execute_is_number.arg_names = ["value"]

	def execute_is_string(self, exec_ctx):
		is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
		return RTResult().success(Number.true if is_number else Number.false)
	execute_is_string.arg_names = ["value"]

	def execute_is_list(self, exec_ctx):
		is_number = isinstance(exec_ctx.symbol_table.get("value"), List)
		return RTResult().success(Number.true if is_number else Number.false)
	execute_is_list.arg_names = ["value"]

	def execute_is_function(self, exec_ctx):
		is_number = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
		return RTResult().success(Number.true if is_number else Number.false)
	execute_is_function.arg_names = ["value"]

# Add an element to the list with a function!
	def execute_append(self, exec_ctx):
		list_ = exec_ctx.symbol_table.get("list")
		value = exec_ctx.symbol_table.get("value")

		if not isinstance(list_, List):
			return RTResult().failure(RTError(
				self.pos_start, self.pos_end,
				"First argument must be list",
				exec_ctx
			))

		list_.elements.append(value)
		return RTResult().success(Number.null)
	execute_append.arg_names = ["list", "value"]

# Get rid of the last element in a list
	def execute_pop(self, exec_ctx):
		list_ = exec_ctx.symbol_table.get("list")
		index = exec_ctx.symbol_table.get("index")

		if not isinstance(list_, List):
			return RTResult().failure(RTError(
				self.pos_start, self.pos_end,
				"First argument must be list",
				exec_ctx
			))

		if not isinstance(index, Number):
			return RTResult().failure(RTError(
				self.pos_start, self.pos_end,
				"Second argument must be number",
				exec_ctx
			))

		try:
			element = list_.elements.pop(index.value)
		except:
			return RTResult().failure(RTError(
				self.pos_start, self.pos_end,
				'Element at this index could not be removed from list because index is out of bounds',
				exec_ctx
			))
		return RTResult().success(element)
	execute_pop.arg_names = ["list", "index"]

	def execute_extend(self, exec_ctx): # Combine two lists
		listA = exec_ctx.symbol_table.get("listA")
		listB = exec_ctx.symbol_table.get("listB")

		if not isinstance(listA, List):
			return RTResult().failure(RTError(
				self.pos_start, self.pos_end,
				"First argument must be list",
				exec_ctx
			))

		if not isinstance(listB, List):
			return RTResult().failure(RTError(
				self.pos_start, self.pos_end,
				"Second argument must be list",
				exec_ctx
			))

		listA.elements.extend(listB.elements)
		return RTResult().success(Number.null)
	execute_extend.arg_names = ["listA", "listB"]	

	def execute_length(self, exec_ctx): # get the length of a list, starting at one
		list_ = exec_ctx.symbol_table.get("list")

		if not isinstance(list_, List):
			return RTResult().failure(RTError(
				self.pos_start, self.pos_end,
				"Argument must be list",
				exec_ctx
			))

		return RTResult().success(Number(len(list_.elements)))
	execute_length.arg_names = ["list"]

# Commands
	def execute_run(self, exec_ctx): # the RUN("") Command!!!!!!!
		fn = exec_ctx.symbol_table.get("fn")

		if not isinstance(fn, String):
			return RTResult().failure(RTError(
				self.pos_start, self.pos_end,
				"Second argument must be string",
				exec_ctx
			))

		fn = fn.value
		try:
			with open(fn, "r") as f:
				script = f.read()
		except Exception as e:
			return RTResult().failure(RTError(
				self.pos_start, self.pos_end,
				f"Failed to load script \"{fn}\"\n" + str(e),
				exec_ctx
			))

		_, error = run(fn, script)
		
		if error:
			return RTResult().failure(RTError(
				self.pos_start, self.pos_end,
				f"Failed to finish executing script \"{fn}\"\n" +
				error.as_string(),
				exec_ctx
			))

		return RTResult().success(Number.null)
	execute_run.arg_names = ["fn"]





#######################################
# CONTEXT
# Tells Spindle where it's at - whether it's in a file, function, or just running normally.
#######################################

class Context:
	def __init__(self, display_name, parent=None, parent_entry_pos=None):
		self.display_name = display_name
		self.parent = parent
		self.parent_entry_pos = parent_entry_pos
		self.symbol_table = None

#######################################
# SYMBOL TABLE
# Keeps track of varibles, lists, functions and their values
#######################################		
class SymbolTable:
	def __init__(self, parent = None):
		self.symbols = {}
		self.parent = parent

	def get(self, name):
		value = self.symbols.get(name, None)
		if value == None and self.parent:
			return self.parent.get(name)
		return value
	
	def set(self, name, value):
		self.symbols[name] = value
	
	def remove(self, name):
		del self.symbols[name]
#######################################
# INTERPRETER
# Time to actually run the code. Names should tell you what each function does. 
#######################################

class Interpreter:
	def visit(self, node, context):
		method_name = f'visit_{type(node).__name__}'
		method = getattr(self, method_name, self.no_visit_method)
		return method(node, context)

	def no_visit_method(self, node, context):
		raise Exception(f'No visit_{type(node).__name__} method defined')

	###################################
	def visit_Number(self, node, context):
		return RTResult().success(
			Number(node.value).set_context(context).set_pos(node.pos_start, node.pos_end)
		)

	def visit_NumberNode(self, node, context):
		return RTResult().success(
			Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
		)

	def visit_StringNode(self, node, context):
		return RTResult().success(
			String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
		)
	
	def visit_ListNode(self, node, context):
		res = RTResult()
		elements = []

		for element_node in node.element_nodes:
			elements.append(res.register(self.visit(element_node, context)))
			if res.should_return(): return res

		return res.success(
		List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
		)


	def visit_VarAccessNode(self, node, context): # Get the value of a varible
		res = RTResult()
		var_name = node.var_name_tok.value
		value = context.symbol_table.get(var_name)
		if not value:
			return res.failure(RTError(
				node.pos_start, node.pos_end,
				f"'{var_name}' is not defined",
				context
			))
		else:
			value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
			return res.success(value)
		
		
	def visit_VarAssignNode(self, node, context): # Set the value of a varible
		res = RTResult()
		var_name = node.var_name_tok.value
		value = res.register(self.visit(node.value_node, context))

		if res.should_return(): return res

		context.symbol_table.set(var_name, value)
		return res.success(value)

# Visit a binary expression. Handles arithmatic expressions and comparasons. 
	def visit_BinOpNode(self, node, context):
		res = RTResult()
		left = res.register(self.visit(node.left_node, context))
		if res.should_return(): return res
		right = res.register(self.visit(node.right_node, context))
		if res.should_return(): return res

		if node.op_tok.type == TT_PLUS:
			result, error = left.added_to(right)
		elif node.op_tok.type == TT_MINUS:
			result, error = left.subbed_by(right)
		elif node.op_tok.type == TT_MUL:
			result, error = left.multed_by(right)
		elif node.op_tok.type == TT_DIV:
			result, error = left.dived_by(right)
		elif node.op_tok.type == TT_POW:
			result, error = left.powed_by(right)
		elif node.op_tok.type == TT_EE:
			result, error = left.get_comparison_eq(right)
		elif node.op_tok.type == TT_NE:
			result, error = left.get_comparison_ne(right)
		elif node.op_tok.type == TT_LT:
			result, error = left.get_comparison_lt(right)
		elif node.op_tok.type == TT_GT:
			result, error = left.get_comparison_gt(right)
		elif node.op_tok.type == TT_LTE:
			result, error = left.get_comparison_lte(right)
		elif node.op_tok.type == TT_GTE:
			result, error = left.get_comparison_gte(right)
		elif node.op_tok.matches(TT_KEYWORD, 'AND'):
			result, error = left.anded_by(right)
		elif node.op_tok.matches(TT_KEYWORD, 'OR'):
			result, error = left.ored_by(right)
		elif node.op_tok.matches(TT_KEYWORD, "NOT"):
			result, error = left.notted()
		if error:
			return res.failure(error)
		else:
			return res.success(result.set_pos(node.pos_start, node.pos_end))

	def visit_UnaryOpNode(self, node, context): # Allows you to "not" something. 
		res = RTResult()
		number = res.register(self.visit(node.node, context))
		if res.should_return(): return res

		error = None

		if node.op_tok.type == TT_MINUS:
			number, error = number.multed_by(Number(-1))

		elif node.op_tok.matches(TT_KEYWORD, "NOT"):
			number, error = number.notted()

		if error:
			return res.failure(error)
		else:
			return res.success(number.set_pos(node.pos_start, node.pos_end))
		
	def visit_IfNode(self, node, context): # Visit if node
		res = RTResult()
		for condition, expr, should_return_null in node.cases:
			condition_value = res.register(self.visit(condition, context))
			if res.should_return(): return res

			if condition_value.is_true():
				expr_value = res.register(self.visit(expr, context))
				if res.should_return(): return res
				return res.success(Number.null if should_return_null else expr_value)

		if node.else_case:
			expr, should_return_null = node.else_case
			else_value = res.register(self.visit(expr, context))
			if res.should_return(): return res
			return res.success(Number.null if should_return_null else else_value)

		return res.success(Number.null)

	def visit_int(self, node, context):
		# Note, this intentionally does nothing. When the interpreter encounters a number, it looks for a visit_int function. Here it is. 
		pass
	def visit_ForNode(self, node, context):
		res = RTResult()
		elements = []
		#start_value = 0
		start_value =  Number(0)
		start_value.value =  Number(0)
		end_value = res.register(self.visit(node.end_value_node, context))
		if res.should_return(): end_value = 1

		if node.step_value_node:
			step_value = res.register(self.visit(node.step_value_node, context))
			if res.should_return(): return res
		else:
			step_value = Number(1)

		i = start_value.value

		if step_value.value >= 0:
			condition = lambda: int(str(i)) < int(str(end_value.value))
		else:
			condition = lambda: i > end_value.value
		
		while condition():
			context.symbol_table.set(node.var_name_tok.value, Number(i))
			i = int(str(i))
			i += int(str(step_value.value))

			value = (res.register(self.visit(node.body_node, context)))
			if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res
			if res.loop_should_continue:
				continue
			if res.loop_should_break:
				break
			elements.append(value)
		return res.success(
			Number.null if node.should_return_null else
			List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

	def visit_WhileNode(self, node, context):
		res = RTResult()
		elements = []
		while True:
			condition = res.register(self.visit(node.condition_node, context))
			if res.should_return(): return res

			if not condition.is_true(): break

			value = res.register(self.visit(node.body_node, context))
			if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

			if res.loop_should_continue:
				continue
			if res.loop_should_break:
				break
			elements.append(value)
		return res.success(
			Number.null if node.should_return_null else
			List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

	def visit_FuncDefNode(self, node, context):
		res = RTResult()

		func_name = node.var_name_tok.value if node.var_name_tok else None
		body_node = node.body_node
		arg_names = [arg_name.value for arg_name in node.arg_name_toks]
		func_value = Function(func_name, body_node, arg_names, node.should_auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)
		
		if node.var_name_tok:
			context.symbol_table.set(func_name, func_value)

		return res.success(func_value)

	def visit_CallNode(self, node, context):
		res = RTResult()
		args = []

		value_to_call = res.register(self.visit(node.node_to_call, context))
		if res.should_return(): return res
		value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

		for arg_node in node.arg_nodes:
			args.append(res.register(self.visit(arg_node, context)))
			if res.should_return(): return res

		return_value = res.register(value_to_call.execute(args))
		if res.should_return(): return res
		return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
		return res.success(return_value)

	def visit_ReturnNode(self, node, context):
		res = RTResult()
		if node.node_to_return:
			value = res.register(self.visit(node.node_to_return, context))
			if res.should_return(): return res
		else:
			value = Number.null
		return res.success_return(value)

	def visit_ContinueNode(self, node, context):
		return RTResult().success_continue()

	def visit_BreakNode(self, node, context):
		return RTResult().success_break()

#######################################
# SET THE DEFAULT VALUES OF THINGS
#######################################

# Map builtin functions to their class counterparts.

BuiltInFunction.input       = BuiltInFunction("input")
BuiltInFunction.clear       = BuiltInFunction("clear")
BuiltInFunction.is_number   = BuiltInFunction("is_number")
BuiltInFunction.is_string   = BuiltInFunction("is_string")
BuiltInFunction.is_list     = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append      = BuiltInFunction("append")
BuiltInFunction.pop         = BuiltInFunction("pop")
BuiltInFunction.extend      = BuiltInFunction("extend")
BuiltInFunction.display      = BuiltInFunction("display")
BuiltInFunction.length      = BuiltInFunction("length")
BuiltInFunction.run      = BuiltInFunction("run")


global_symbol_table = SymbolTable()
global_symbol_table.set("NULL", Number.null)
global_symbol_table.set("FALSE", Number.false)
global_symbol_table.set("TRUE", Number.true)
global_symbol_table.set("MATH_PI", Number.math_PI) #Varible
# MAP BUILT IN FUNCTIONS TO WHAT THEY'LL LOOK LIKE IN SPINDLE
global_symbol_table.set("DISPLAY", BuiltInFunction.display)
global_symbol_table.set("INPUT", BuiltInFunction.input)
global_symbol_table.set("CLEAR", BuiltInFunction.clear)
global_symbol_table.set("CLS", BuiltInFunction.clear)
global_symbol_table.set("IS_NUM", BuiltInFunction.is_number)
global_symbol_table.set("IS_STR", BuiltInFunction.is_string)
global_symbol_table.set("IS_LIST", BuiltInFunction.is_list)
global_symbol_table.set("IS_FUN", BuiltInFunction.is_function)
global_symbol_table.set("APPEND", BuiltInFunction.append)
global_symbol_table.set("POP", BuiltInFunction.pop)
global_symbol_table.set("EXTEND", BuiltInFunction.extend)
global_symbol_table.set("LENGTH", BuiltInFunction.length)
global_symbol_table.set("RUN", BuiltInFunction.run)

#######################################
# SEMI PARSER
# Generally, this is not apart of the actual Spindle language runtime, but it serves to help it.
# It also fixes many bugs in regards to inconsistances in the text. 
# semi_parse_string(): This is a helper function. It takes in the string entered into the program and semi parses it. Effectivly fixing the issue with PROCEDURE
#######################################
def semi_parse_string(string):
    """Divides the given string into a list of strings based on PROCEDURE keywords and curly brace nesting, adding missing ELSE blocks to IF statements.

    Args:
        string: The input string to be divided.

    Returns:
        A list of strings, where each string is a separate procedure or code block with added ELSE blocks.
    """

    result = []
    current_block = []
    brace_depth = 0
    in_if_block = False

    for line in string.splitlines():
        if line.startswith("PROCEDURE"):
            if current_block:
                result.append("".join(current_block))
            current_block = [line + " \n "]
            brace_depth = 0
            in_if_block = False
        else:
            current_block.append(line + " \n ")
            if "{" in line:
                brace_depth += line.count("{")
            if "}" in line:
                brace_depth -= line.count("}")
            if brace_depth == -1:
                if in_if_block:
                    # Add an empty ELSE block if the IF block doesn't have one
                    current_block.append("ELSE {}\n")
                result.append("".join(current_block))
                current_block = []
                in_if_block = False
            elif line.strip().startswith("IF"):
                in_if_block = True

    if current_block != []:
        if in_if_block:
            current_block.append("ELSE {}\n")
        result.append("".join(current_block))

    return result
# This function addes an empty ELSE block to if statements that don't already have one. This is required for them to work correctly.
def add_else_to_if(text):
    found_if = False
    return_text = ""
    for i in range(len(text)):
        char = text[i]
        return_text += char
        if char == " ":
            continue
        #looking for if
        if char == "I" and text[i+1]=="F":
            found_if = True
        if char == "}" and found_if == True:
            #look for an else
            found_else = False
            for j in range(len(text[i:])):
                ochar = text[i+j]
                if ochar == "E" and text[i+j+1] == "L" and text[i+j+2] == "S" and  text[i+j+3] == "E":
                    found_else = True
                    found_if = False
                    break
                if ochar =="}":
                    return_text += " ELSE{ \n }"
                    found_if = False

    return return_text


# This function handles RUN commands and calls the run_program for each semi parse generated by the semi_parse_string function
# this function DOES NOT actually run the program, just the text it was given. 
def run(fn, text):
	program_text = ""
	proc_flag = False
	if text.strip() == "":
		return

    # Create tokens just for the sake of figuring out wheter we're dealing with a RUN command or a procedure
	tokens = generate_tokens('<stdin>', text)
	if str(tokens[0]) == "IDENTIFIER:RUN": # Test wheter the current script has a RUN FILE function
		text = str(get_file_text(str(tokens[2]).split(":")[1])).replace("{","{ \n")
	else: 
		text = text.replace("{","{ \n")
    # Test wheter or not code contains a function.
	if "PROCEDURE" in text: # There's a procedure!!! Use sublists
		proc_flag = True
		program_text = semi_parse_string(text)
	else :
		# Check if there's already an ELSE block in the code
		if "ELSE" in text:
			program_text = semi_parse_string(text)[0]
		else:
			program_text = semi_parse_string(add_else_to_if(text))[0]
		# Convert text to tokens for the else statement inserition
		result,error = run_program('<stdin>', program_text)
		if error: 
			display_res(error.as_string())

	if proc_flag:
		proc_flag = False
		for i in range(len(program_text)): # Run each part of the text seperatly
			if program_text[i].strip() == "":
				continue
			# Check if there's already an ELSE block in this part
			if "ELSE" in program_text[i]:
				result,error = run_program('<stdin>', program_text[i])
			else:
				result,error = run_program('<stdin>', add_else_to_if(program_text[i]))
			if error: 
				display_res(error.as_string())
				break


# Runs the program given to it by the programmer. This function is called by the run function and actually "runs" the program
def run_program(fn, text):
	if not isinstance(text, list):
	# Generate tokens
		lexer = Lexer(fn, text)
		tokens, error = lexer.make_tokens()
		#print(tokens) # <-- for debug purposes
		if error: return None, error
	else:
		tokens = text
	
	# Generate AST
	parser = Parser(tokens)
	ast = parser.parse()

	if ast.error: return None, ast.error

	# Run program
	interpreter = Interpreter()
	context = Context('<program>')
	context.symbol_table = global_symbol_table
	result = interpreter.visit(ast.node, context)

	return result.value, result.error

def generate_tokens(fn,text):
	lexer = Lexer(fn, text)
	tokens, error = lexer.make_tokens()
	return tokens

def get_file_text(file_name): # Get the text of a file, used by the RUN("") command.
	try:
		with open(file_name, "r") as f:
			script = f.read()
			return script
	except Exception as e:
		return "Error"
# The home of the logic for the RUN("") command
def execute_run(self, exec_ctx):
		fn = exec_ctx.symbol_table.get("fn")

		if not isinstance(fn, String):
			return RTResult().failure(RTError(
				self.pos_start, self.pos_end,
				"Second argument must be string",
				exec_ctx
			))

		fn = fn.value

		try:
			with open(fn, "r") as f:
				script = f.read()
		except Exception as e:
			return RTResult().failure(RTError(
				self.pos_start, self.pos_end,
				f"Failed to load script \"{fn}\"\n" + str(e),
				exec_ctx
			))

		_, error = run(fn, script)
		
		if error:
			return RTResult().failure(RTError(
				self.pos_start, self.pos_end,
				f"Failed to finish executing script \"{fn}\"\n" +
				error.as_string(),
				exec_ctx
			))

		return RTResult().success(Number.null) 
