# Holds the code for the lanague
#######################################
# IMPORTS
#######################################
from strings_with_arrows import *
#################################
# ------------------ CONSTANTS 
##################################
DIGITS = "0123456789"

#################################
# ------------------ ERRORS 
##################################

class Error:
    def __init__(self,pos_start,pos_end,error_name,details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result = "\n[*** Error! ***] \n"
        result += f' -- Summary:\n'
        result += f'  Type: {self.error_name} | Details: {self.details}'
        result += f'\n -- Location:\n'
        result += f'  File: {self.pos_start.fn} | Line: {self.pos_start.ln + 1} \n'
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        result += "----------\n"
        
        return result

class IllegalCharError(Error):
    def __init__(self,pos_start,pos_end, details):
        super().__init__(pos_start,pos_end,"Illegal Character",details)

# Error in the parsing process
class InvalidSyntaxError(Error):
    def __init__(self,pos_start,pos_end, details=' '):
        super().__init__(pos_start,pos_end,"Invalid Syntax",details) 
# You CANNOT divide by 0
class RTError(Error):
    def __init__(self,pos_start,pos_end, details=' '):
        super().__init__(pos_start,pos_end,"Runtime Error",details)                

#################################
# ------------------ POSITION 
# idx: index
# ln: line number
# col: Collum number
#fn:file_name
# ftxt: file_text
##################################
class Position:
    def __init__(self, idx, ln,col,fn, ftxt):
        self.fn = fn
        self.ftxt = ftxt
        self.idx = idx
        self.ln = ln
        self.col = col
    def advance(self,current_char=None):
        self.idx +=1
        self.col +=1

        if current_char == "\n":
            self.ln += 1
            self.col = 0
        return self
    
    def copy(self):
        return Position(self.idx, self.ln,self.col,self.fn, self.ftxt)

#################################
# ------------------ TOKENS 
# TT: Token Type
# EOF: End of File
##################################
TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_EOF = "EOF"

class Token:
    def __init__(self,type_,value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        if pos_end:
            self.pos_start = pos_start.copy()    
            
    def __repr__ (self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
    

#################################
# ------------------ Lexer 
##################################
class Lexer:
    def __init__(self,fn,text):
            self.fn = fn
            self.text = text
            self.pos = Position(-1,0,-1,fn,text)
            self.current_char = None
            self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
                
            # Handle Numbers
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == "+":
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == "-":
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == "*":
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == "/":
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            else:
                # We don't find the charahcter we're looking for, return an error
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start,self.pos,"'"+char+"'")
        
        tokens.append(Token(TT_EOF,pos_start=self.pos))
        return tokens, None

    def make_number(self):
        num_str= ""
        dot_count = 0
        pos_start = self.pos.copy()
        while self.current_char != None and self.current_char in DIGITS + ".":
            if self.current_char == ".":
                if dot_count == 1: 
                    break
                dot_count += 1
                num_str += "."
            else:
                num_str += self.current_char
            self.advance()    
            
        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start,self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start,self.pos)

 #################################
# ------------------ Nodes 
# tok: token
##################################
class NumberNode:
    def __init__(self,tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'
    
 # Binary Opperation Node   
# op_tok: Operation token

class BinOpNode:
    def __init__(self,left_node, op_tok,right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'
    
class UnaryOpNode:
    def __init__(self, op_tok, node) :
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):  
        return f'({self.op_tok}, {self.node})'  
            
#################################
# ------------------ PARSER RESULTS
# res = result
##################################     
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self,res):
        if isinstance(res, ParseResult):
            if res.error:
                self.error = res.error

            return res.node
        
        return res

    def success(self,node):
        self.node = node
        return self

    def failure(self,error):
        self.error = error
        return self

#################################
# ------------------ PARSER 
##################################    
class Parser:
    def __init__(self,tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self, ):
        self.tok_idx += 1
        if self.tok_idx  < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError
                (self.current_tok.pos_start,self.current_tok.pos_end,
                "Expected '+', '-', '*' or '/'"
                ))
        return res
########################################################
    def factor(self):
        res = ParseResult()
        tok = self.current_tok
        if tok.type in (TT_PLUS, TT_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error: 
                return res
            return res.success(UnaryOpNode(tok, factor))

        elif tok.type in (TT_INT,TT_FLOAT):
            res.register(self.advance())
            return res.success(NumberNode(tok))
        
        elif tok.type == TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error: 
                return res

            if self.current_tok.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError
                (self.current_tok.pos_start,self.current_tok.pos_end,
                "Expected ')'"
                ))


        return res.failure(
            InvalidSyntaxError(tok.pos_start,tok.pos_end,"Expected int or float")
            )

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def bin_op(self,func,ops):
        res = ParseResult()
        left = res.register(func())
        if res.error:
            return res
        
        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)
#################################
# ------------------ RUNTIME RESULT 
##################################
class RTResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):
        if res.error:
            self.error = res.error  
        return res.value
    
    def success(self, value):
        self.value = value
        return self
    
    def failure(self, error):
        self.error = error
        return self

#################################
# ------------------ VALUES 
##################################
class Number:
    def __init__(self,value):
        self.value = value
        self.set_pos()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value), None

    def subtracted_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value), None    
    
    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value), None

    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end, "Division by zero!"
                )
            return Number(self.value / other.value), None  
    
    def __repr__(self):
        return str(self.value)
#################################
# ------------------ INTERPRETER 
##################################
class Interpreter:
    def visit(self, node):
        method_name= f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)
    
    def no_visit_method(self, node):
        raise Exception(f'No visit_{type(node).__name__} method defined!')
###############################################################
    def visit_NumberNode(self, node):
        return RTResult().success(
            Number(node.tok.value).set_pos(node.pos_start, node.pos_end)
        )

    def visit_BinOpNode(self, node):
        res = RTResult()
        left = res.register(self.visit(node.left_node))
        if res.error: 
            return res
        right = res.register(self.visit(node.right_node))  
        if res.error: 
            return res
        
        if  node.op_tok.type ==TT_PLUS:
            result, error = left.added_to(right)
        elif  node.op_tok.type ==TT_MINUS:
            result, error = left.subtracted_by(right)
        elif  node.op_tok.type ==TT_MUL:
            result, error = left.multed_by(right)
        elif  node.op_tok.type ==TT_DIV:
            result, error = left.dived_by(right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node):
        res = RTResult()
        number = res.register(self.visit(node.node))  
        if res.error: 
            return res
        
        error = None

        if node.op_tok.type == TT_MINUS:
            number, error = number.multed_by(Number(-1))

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))
#################################
# ------------------ RUN 
##################################
def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return  None, error
# Generate Abtract Syntax Tree
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error
    
    #run program
    interpreter = Interpreter()
    result = interpreter.visit(ast.node)
    return result.value, result.error
