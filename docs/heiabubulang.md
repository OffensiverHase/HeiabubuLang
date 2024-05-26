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
Yet some times it's good practise to specify the type yourself, for better readability   
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
 - if the body of the if only contains one statement you can use a colon `:` like with function bodies
 - you check for equality with a single equals `=`
 - the if block will be run if the condition evaluates to true, else the else block gets run
 - you don't have to specify an else block, the programm continues with the next statement after the if

### While ###
While is used to execuate a code block while a condition is `true`
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
you can also specify a step size.
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
You can declare functions with the `fun` keyword
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

## Classes and Objects ##

## Operators ##

## Other ##
