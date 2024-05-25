from sys import exit


def fib(num: int) -> int:
    if num <= 1:
        return num
    else:
        return fib(num - 1) + fib(num - 2)


exit(fib(46))

# 10:
# runtime 0.018s

# 46:
# runtime 5m 39.094s
