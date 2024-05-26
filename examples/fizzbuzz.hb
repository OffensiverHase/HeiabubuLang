fun fizzbuzz() {
    for i <- 1 .. 101 {
        if i % 3 = 0 & i % 5 = 0:
            print('FizzBuzz\n')
        else:
            if i % 3 = 0:
                print('Fizz\n')
            else:
                if i % 5 = 0:
                    print('Buzz\n')
                else:
                    print('%i\n', i)
    }
}

fun main():
    fizzbuzz()