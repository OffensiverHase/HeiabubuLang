# Heiabubu #
Heiabubu is a LLVM based in developement language designed to write high performace programms. 
This is archieved by omitting some runtime checks, what sadly makes programming in this language a bit harder.

## Beginning ##

### Hello world ###
Here is a simple programm that prints `Hello, World!`:
```python
fun main() {
    print('Hello, World!\n')
}
```
Since this function only consists of one statement this can be simplified:
```python
fun main():
    print('Hello, World\n')
```
When running the JIT compiler this can be simplified even more:
```python
print('Hello, World!\n')
```
 - `fun` is used to declare a function
 - the `main()` function the entry point of your programm. If it's not there the JIT compiler will start at the top level
 - the body of a function is inside curly braces `{}`, but if it's only one statement this can come after a colon `:`
 - `print` works just like c printf and prints to stdout

## Variables, Values and Types ## 

### Variables ###
Just like in every other language variables are used to store data. Variables are always mutable.
```python
x <- 5 
y: int <- x * 4
z: float <- 'hello'  # will fail compilation, because you cannot store a str to a float
```
 - the assign operator is an arrow `<-`
 - variables are declared nearly like in python: `name <- value`
 - you can annotate variables with types `name: type <- value`

Variables are deleted when the scope they were declared in is removed:
```python
for i <- 0 .. 10 {
    sq <- i * i
    print('%i\n', sq)
}
print('at the end it was %i\n', sq)  # will throw an error during compilation
```

### Types ###
Every variable in Heiabubu has a data type, but for variables Heiabubu can always infer the data type.
In the previous example you don't have to write `sq: int <- i * i`, because Heiabubu sees that i is an `int` and an `int` times an `int` is still an int.
Yet some times it's good practise to specify the type yourself, for better readability.   
Heiabubu has the following types:
 - `int` A basic type for integer values with 32 bits
 - `byte` A type for integer values with 8 bits (Not fully implemented yet)
 - `float` A basic type for floating point values with 64 bits
 - `bool` A basic type for boolean values `true` and `false` with 1 bit
 - `str` A basic type for character string values, a list of `byte`s
 - `list<type>` A basic type for array like lists, a list of `type`s
 - User defined types used for objects of classes


### Lists ###
One really useful data structure is just a simple list or array.
Heiabubu has still a very experimental approach to lists.
You can't specify the size of a list, so it's best practise to initialise it with default values.
Also Heiabubu has no index out of bounds error, so lists can lead to undefined behaviour sometimes
```python
x <- []  # Not recommended, will not allocate any space for elements
y <- [0,0,0,0]  # is better for a list with a size of 4
x[0] <- 1  # Yet possible
y[4]  # Possible aswell
z: list<int> <- x + y  # Concat two lists is not implemented yet but is in progress
```
Strings are also just a list of `byte`s, so everything that works with lists also applies to `str`.

## Control flow ##
Like other programming languages Heiabubu is capable of changing the control flow on expressions being evaluated to true.

### If ###
`if` statements are used to execute a block of code bsed on a condition.
```python
if 1 = 1:
    print('Your computer works just fine!\n')
else {
    print('Your computer is broken\n!)
    return 1
}
```
 - the syntax for `if` statements is `if condition {body}`
 - if the body of the if only contains one statement you can use a colon `:` like with any other bodies
 - bodies can not be empty, use the `pass` keyword to insert a no-op that will be removed during optimisation
 - you check for equality with a single equals `=`
 - the if block will be run if the condition evaluates to true, else the else block gets run
 - you don't have to specify an else block, the programm continues with the next statement after the if

### While ###
While is used to execuate a code block while a condition is `true`:
```python
a <- 0
while a < 10 {
    print('a is %i\n', a)
    a <- a + 1
}
```
 - the syntax for `while` statements is `while condition {body}`
 - the same rules as on if and functions can be applied for a while body
 - check smaller than with `<`
 - while the condition is true the body is run

### For ###
For loops are used if you want to do a thing for a certain amount of times.
The above example can be simplified as the following:
```python
for a <- 0 .. 10:
    print('a is %i\n', a)
```
you can also specify a step size:
```python
for a <- 0 .. 10 step 2:
    print('a is %i\n', a)
```
 - the syntax for `for` statements is `for name <- start .. to`
 - you can specify step size like `for name <- start_value .. to_value step step_value`
 - the same rules as on if, functions and `while` can be applied for a for body

### Break and Continue ###
In loops you can use the `break` or the `continue` statement.
`break` will break out of the current loop and `continue` will continue with the next iteration.

    
## Functions ##
You can declare functions with the `fun` keyword:
```python
fun plus_one(number: int) -> int:
    return number + 1
    
fun main() {
    a <- 1
    a <- plus_one(a)
    print('Result is %i\n', a)
}
```
 - function parameters are written within parameters
 - each parameter has to have a type
 - multiple parameters are seperated by commas `,`
 - the return type of the function is specified after the function's parentheses, after an arrow `->`
 - if the return type is omitted 'null' is used
 - the body of a function uses the same rules as any other bodies
 - heiabubu does not support first class or higher order functions
 - top level code is put into an auto-generated function called `load_filename`, that has return type of `int`:
```python
# file called hello.hb
fun main() {
    print('Hello from main\n')
    x <- load_hello()
    print('load_hello() returned %i\n', x)
}

print('Hello from top level\n')
return 1  # Default to 0 if ommitted
```

This will output:
>   Hello from main  
>   Hello from top level  
>   load_hello() returned 1  

## Classes and Objects ##
Heiabubu supports object-oriented programming with classes and objects.
Objects are useful for storing data in your program.
Classes allow you to declare a set of characteristics for an object.
When you create objects from a class, you can save time and effort because you don't have to declare these characteristics every time.
### Classes ###
You can declare classes with the `class` keyword:
```python
class Person {
    name: str
    age: int
    programmmer: bool
    
    fun create(name: str, age: int) {
        self.name = name
        self.age = age
    }
    
    fun make_programmer():
        self.programmer = true
}
```
 - classes can have properties and methods
 - declare properties with `name: type`
 - declare methods just like normal functions
 - self referres to the instance, just like in python
 - method create is used as the constructor and is added automatically with empty body if omitted
 - uninitialised properties contain undefined and may lead to undefined behaviour

### Objects ###
```python
p <- Person('john', 25)  # creates an instance of Person and then calls create
print('And his name is ... %s\n', p.name)
p.age <- 26
print('Now %ss age is %i\n', p.name, p.age)
p.make_programmer()
print('Now he is a programmer: %i\n', p.programmer)  # bools are represented as 0 (false) and 1 (true)
```

## Operators and Keywords ##

### Arithmatic Operators ###
 - `+` Addidtion
 - `-` Subtraction
 - `*` Multiplication
 - `/` Division
 - `^` Exponent
 - `%` Modulus

### Comparison Operators ###
 - `<`  Less-than
 - `>`  Greater than
 - `<=` Less-equal
 - `>=` Greater-equal
 - `<>` Not-equal
 - `=`  Equal

### Assignment Operators ###
 - `<-` Assign
 - Work in progress

### Prefix Operators ###
 - `!` Not
 - `-` Minus

### Keywords ###
 - `if` if statement declaration
 - `else` else block declaration
 - `for` for statement declaration
 - `step` change step size of for loop
 - `while` while statement declaration
 - `fun` function declarations
 - `return` return out of a function
 - `break` break out of a loop
 - `continue` continue with the next loop iteration
 - `class` class declaration
 - `pass` no-op statement for empty blocks
 - `import` import other files

## Other ##

### Imports ###
Import other files, for now they have to be in the same directory.
```python
import other  # will import ./other.hb

fun main():
    function_in_other_file()
```
### Newlines and Whitespace ###
Statements are finished with a newline character, but else newlines and whitespaces shouldn't matter.
If you want to write multiple statements in the same line, you can use a semicolon `;`




[Jump to the top](https://github.com/OffensiverHase/HeiabubuLang/blob/master/docs/heiabubulang.md#Heiabubu)
# Speed! #
![Speed!](https://www.carsuk.net/wp-content/uploads/2009/07/Clarkson-Atom.jpg)
