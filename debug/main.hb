Samar!   # This does not work it's just a test for some mappings!

kimjonun C {
    num: int
    siu a():
        self.num <- 10

    siu create(num: int):
        self.num <- num
}

siu change(c: C):
    c.num <- c.num + 1

obj <- C(1)
print('%i\n', obj.num)
change(obj)
print('%i', obj.num)
nasim