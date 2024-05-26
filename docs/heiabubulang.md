# Heiabubu #
Heiabubu is a LLVM based in developement language designed to write high performace programms. 
This is archieved by omitting some runtime checks, what sadly makes programming in this language a bit harder.

## Beginning ##

### Hello world ###
Here is a simple programm that prints `Hello, World!`:
```kotlin
fun main() {
    print('Hello, World!')
}
```
Since this function only consists of one statement this can be simplified:
```kotlin
fun main():
    print('Hello, World')
```
When running the JIT compiler this can be simplified even more:
```kotlin
print('Hello, World!')
```
 - `fun` is used to declare a function
 - the `main()` function the entry point of your programm. If it's not there the JIT compiler will start at the top level
 - the body of a function is inside curly braces `{}`, but if it's only one statement this can come after a colon `:`
 - `print` works just like c printf and prints to stdout

## Variables, Values and Types ## 

### Variables ###
Just like in every other language variables are used to store data. Variables are always mutable.
```kotlin
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
    print('%i', sq)
}
print('at the end it was %i', sq)  # will throw an error during compilation
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
Strings are also just a list of `byte`s, so everything that works with lists also applies to `str`

## Control flow ##
Like other programming languages Heiabub is capable of changing the control flow on expressions being evaluated to true.


## Classes and Objects ##

## Operators ##

## Other ##
