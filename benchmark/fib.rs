use std::process;

fn fib(num: i32) -> i32 {
    if num <= 1 {
        return num
    } else {
        return fib(num - 1) + fib(num - 2)
    }
}

fn main() {
    process::exit(fib(46));
}

// 10:
// compilation 0.271s
// runtime 0.001s

// 46:
// compilation 0.184
// runtime 21.596s