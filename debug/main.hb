class C {
    num: int
    fun a():
        self.num <- 10

    fun create(num: int):
        self.num <- num
}

fun change(c: C):
    c.num <- c.num + 1

obj <- C(1)
print('%i\n', obj.num)
change(obj)
print('%i', obj.num)
return