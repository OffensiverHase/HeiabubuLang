int fib(int num) {
    if (num <= 1) {
        return num;
    } else {
        return fib(num - 1) + fib(num - 2);
    }
}

int main() {
    return fib(46);
}

// 10:
// compilation 0.071s
// runtime 0.002s

// 46:
// compilation 0.073s
// runtime 16.283s