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
```python
print('Hello, World!')
```
 - `fun` is used to declare a function
 - the `main()` function the entry point of your programm. If it's not there the JIT compiler will start at the top level
 - 
