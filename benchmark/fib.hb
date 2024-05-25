fun fib(num: int) -> int {
    if num <= 1:
        return num
    else:
        return fib(num - 1) + fib(num - 2)
    return 0
}

fun main() -> int:
    return fib(46)

# 10:
# compilation 1.434s
# runtime 0.001s

# 46:
# compilation 1.438s
# runtime 8.590s