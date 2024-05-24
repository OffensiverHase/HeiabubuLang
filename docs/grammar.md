# The heia bubu grammar

### __program__:
    each entry represents one file
  - __statements__?

### __statements__:
    list of statements representing and containing a scope
  - __statement__+
 
### __ident__:
    identifiers for holding values as variables, classes or functions
  - [a-zA-Z] ([a-zA-Z1-9_$])*
 
### __int__:
    simple integer value representation
  - [0-9]*
 
### __float__:
    simple floating point value representation
  - [0-9]* '.' [0-9]*
 
### __type__: 
    types for type annotations, allowing identifiers for self defined types
  - int
  - float
  - bool
  - null
  - str
  - byte
  - list '<' __type__ '>'
  - __ident__
 
### __body_expression__: 
    used for bodies of functions, if statements and loops, allow single line after :
  - '{' __statements__ '}'
  - ':' __statement__

### __statement__:
    single line statement that is not guaranteed to have a value, broadest clause
  - __while__
  - __for__
  - __fun_def__
  - __class_def__
  - __var__assign__
  - 'pass'
  - 'return' __expression__?
  - 'break'
  - 'continue'
  - 'import' __ident__
  - __expression__
 
### __expression__:
    single line statement that is guaranteed to have a value
    broadest value clause
    bitwise operations on two compare expressions
  - __comp_expr__ ('&' | '|' | '~') __comp_expr__
  - __comp_expr__
 
### __comp_expr__:
    expression for comparing two arithmatic expressions
  - '!' __comp_expr__
  - __arithm_expr__ ('=' | '<>' | '<' | '>' | '<=' | '>=') __arithm_expr__
  - __arithm_expr__
 
### __arithm_expr__:
    broadest arithmatic expression
  - __term__ ('+' | '-') __term__
  - __term__
 
### __term__:
    term for multipling, dividing and remainders
  - __factor__ ('*' | '/' | '%') __factor__
  - __factor__
 
### __factor__:
    factor for unary operations
  - ('+' | '-') __factor__
  - __power__
 
### __power__:
    power function and list value set and get
  - __atom__ '[' __expression__ ']' 
  - __atom__ '[' __expression__ ']' '<-' __expression__
  - __atom__ '^' __atom__ 
  - __atom__
 
### __atom__:
    lowest form of expressions, don't perform calculations, only retrieve direct values
  - __int__
  - __float__
  - __ident__
  - __fun_call__
  - __ident__ '.' __ident__
  - __ident__ '.' __ident__ '<-' __expression__
  - __ident__ '.' __fun_call__
  - '(' __expression__ ')'
  - ''' (utf-8)* '''
  - '[' __atom__? (',' __atom__)* ']'
  
### __if__:
    simple conditional branching
  - 'if' __expression__ __body_expression__
  - 'if' __expression__ __body_expression__ 'else' __body_expression__

### __fun_def__:
    function definitions
  - 'fun' __ident__ '(' (__ident__ __type__)? (',' __ident__ __type__)* ')' ('->' __type__)? __body_expression__
 
### __while__:
    simple while loop
  - 'while' __expression__ __body_expression__
 
### __for__:
    for loop with iteration over integer range
  - 'for' __ident__ '<-' __factor__ '..' __arithm_expr() ('step' __factor__)? __body_expression__
 
### __class_def__:
    class definitions
  - 'class' __ident__ '{' ((__ident__ ':' __type__) | __fun_def__)? (',' ((__ident__ ':' __type__) | __fun_def__))* '}'
 
### __var_assign__:
    variable assignments
  - __ident__ (':' __type__)? '<-' __expression__
 
### __fun_call__:
    function calls
  - __ident__ '(' __expression__? (',' __expression__)* ')'