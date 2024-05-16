; ModuleID = "main_main"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"A" = type {i32}
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
  %"A" = alloca %"A"
  %"obj" = alloca %"A"*
  %"A.x_ptr" = getelementptr %"A", %"A"* %"A", i32 0, i32 0
  store i32 420, i32* %"A.x_ptr"
  store %"A"* %"A", %"A"** %"obj"
  %"obj.1" = load %"A"*, %"A"** %"obj"
  call void @"hell_yeah"(%"A"* %"obj.1")
  %"nop" = add i32 0, 0
  %"obj.2" = load %"A"*, %"A"** %"obj"
  call void @"hell_yeah"(%"A"* %"obj.2")
  ret i32 0
}

define i32* @"lst"(i32 %".1", i32 %".2")
{
lst_entry:
  %"list_ptr" = alloca [2 x i32]
  %"elem1" = alloca i32
  %"elem2" = alloca i32
  store i32 %".1", i32* %"elem1"
  store i32 %".2", i32* %"elem2"
  %"elem1.1" = load i32, i32* %"elem1"
  %"elem1.2" = load i32, i32* %"elem1"
  %"elem2.1" = load i32, i32* %"elem2"
  %"array.0" = getelementptr [2 x i32], [2 x i32]* %"list_ptr", i32 0, i32 0
  store i32 %"elem1.2", i32* %"array.0"
  %"array.0.1" = getelementptr i32, i32* %"array.0", i32 1
  store i32 %"elem2.1", i32* %"array.0.1"
  %"ret_temp" = getelementptr [2 x i32], [2 x i32]* %"list_ptr", i32 0, i32 0
  ret i32* %"ret_temp"
}

define i32 @"nice"(%"A"* %".1")
{
nice_entry:
  %"self" = alloca %"A"*
  store %"A"* %".1", %"A"** %"self"
  ret i32 69
}

define void @"hell_yeah"(%"A"* %".1")
{
hell_yeah_entry:
  %"c_str" = alloca i8*
  %"c_str.1" = alloca i8*
  %"self" = alloca %"A"*
  store %"A"* %".1", %"A"** %"self"
  %"str_bitcast" = bitcast [5 x i8]* @"__str_0" to i8*
  %"self.1" = load %"A"*, %"A"** %"self"
  %"nice.ret" = call i32 @"nice"(%"A"* %"self.1")
  store i8* %"str_bitcast", i8** %"c_str"
  %"c_str_to_ptr" = bitcast [5 x i8]* @"__str_0" to i8*
  %"printf.ret" = call i32 (i8*, ...) @"printf"(i8* %"c_str_to_ptr", i32 %"nice.ret")
  %"str_bitcast.1" = bitcast [5 x i8]* @"__str_1" to i8*
  %"self.2" = load %"A"*, %"A"** %"self"
  %"A.x_ptr" = getelementptr %"A", %"A"* %"self.2", i32 0, i32 0
  %"A.x" = load i32, i32* %"A.x_ptr"
  store i8* %"str_bitcast.1", i8** %"c_str.1"
  %"c_str_to_ptr.1" = bitcast [5 x i8]* @"__str_1" to i8*
  %"printf.ret.1" = call i32 (i8*, ...) @"printf"(i8* %"c_str_to_ptr.1", i32 %"A.x")
  ret void
}

@"__str_0" = internal constant [5 x i8] c"%i\0a\00\00"
@"__str_1" = internal constant [5 x i8] c"%i\0a\00\00"