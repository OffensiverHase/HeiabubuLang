# Heiabubu #
Heiabubu is a LLVM based in developement language designed to write high performace programms. 
This is archieved by omitting some runtime checks, what sadly makes programming in this language a bit harder.

## Features ##

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
    print('%i', sq)
}
print('at the end it was %i', sq)  # will throw an error during compilation
```
