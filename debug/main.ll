; ModuleID = "main_main"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"C" = type {i32}
declare double @"llvm.pow.f64"(double %".1", double %".2")

declare i32 @"printf"(i8* %".1", ...)

@"true" = constant i1 1
@"false" = constant i1 0
declare i32 @"strlen"(i8* %".1")

declare i8* @"malloc"(i32 %".1")

declare i8* @"strcpy"(i8* %".1", i8* %".2")

define i32 @"load_main"()
{
load_main_entry:
  %"C" = alloca %"C"
  %"obj" = alloca %"C"*
  %"c_str" = alloca i8*
  %"C.num_ptr" = getelementptr %"C", %"C"* %"C", i32 0, i32 0
  store i32 1, i32* %"C.num_ptr"
  store %"C"* %"C", %"C"** %"obj"
  %"obj.1" = load %"C"*, %"C"** %"obj"
  call void @"change.C*"(%"C"* %"obj.1")
  %"str_bitcast" = bitcast [3 x i8]* @"__str_0" to i8*
  %"obj.2" = load %"C"*, %"C"** %"obj"
  %"C.num_ptr.1" = getelementptr %"C", %"C"* %"obj.2", i32 0, i32 0
  %"C.num" = load i32, i32* %"C.num_ptr.1"
  store i8* %"str_bitcast", i8** %"c_str"
  %"c_str_to_ptr" = bitcast [3 x i8]* @"__str_0" to i8*
  %"printf.ret" = call i32 (i8*, ...) @"printf"(i8* %"c_str_to_ptr", i32 %"C.num")
  ret i32 0
}

define void @"C.a.C*"(%"C"* %".1")
{
"C.a.C*_entry":
  %"self" = alloca %"C"*
  store %"C"* %".1", %"C"** %"self"
  %"self.1" = load %"C"*, %"C"** %"self"
  %"C.num_ptr" = getelementptr %"C", %"C"* %"self.1", i32 0, i32 0
  store i32 10, i32* %"C.num_ptr"
  ret void
}

define void @"change.C*"(%"C"* %".1")
{
"change.C*_entry":
  %"c" = alloca %"C"*
  store %"C"* %".1", %"C"** %"c"
  %"c.1" = load %"C"*, %"C"** %"c"
  %"c.2" = load %"C"*, %"C"** %"c"
  %"C.num_ptr" = getelementptr %"C", %"C"* %"c.2", i32 0, i32 0
  %"C.num" = load i32, i32* %"C.num_ptr"
  %"add" = add i32 %"C.num", 1
  %"C.num_ptr.1" = getelementptr %"C", %"C"* %"c.1", i32 0, i32 0
  store i32 %"add", i32* %"C.num_ptr.1"
  ret void
}

define void @"five.i32.i32.i32.i32.i32"(i32 %".1", i32 %".2", i32 %".3", i32 %".4", i32 %".5")
{
five.i32.i32.i32.i32.i32_entry:
  %"one" = alloca i32
  %"two" = alloca i32
  %"three" = alloca i32
  %"four" = alloca i32
  %"five" = alloca i32
  store i32 %".1", i32* %"one"
  store i32 %".2", i32* %"two"
  store i32 %".3", i32* %"three"
  store i32 %".4", i32* %"four"
  store i32 %".5", i32* %"five"
  ret void
}

@"__str_0" = internal constant [3 x i8] c"%i\00"