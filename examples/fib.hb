fun fib(num: int) -> int {
    if num <= 1:
        return num
    else:
        return fib(num - 1) + fib(num - 2)
    return 0
}

fun main() -> int:
    return fib(46)
