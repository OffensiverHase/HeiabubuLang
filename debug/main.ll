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
  %"x" = alloca i8*
  %"A.x_ptr" = getelementptr %"A", %"A"* %"A", i32 0, i32 0
  store i32 420, i32* %"A.x_ptr"
  store %"A"* %"A", %"A"** %"obj"
  %"obj.1" = load %"A"*, %"A"** %"obj"
  call void @"hell_yeah"(%"A"* %"obj.1")
  %"str_ptr1" = getelementptr [3 x i8], [3 x i8]* @"__str_2", i32 0, i32 0
  %"str_ptr2" = getelementptr [4 x i8], [4 x i8]* @"__str_3", i32 0, i32 0
  %"len1" = call i32 @"strlen"(i8* %"str_ptr1")
  %"len2" = call i32 @"strlen"(i8* %"str_ptr2")
  %".4" = add i32 %"len1", %"len2"
  %"concat_ptr" = call i8* @"malloc"(i32 %".4")
  %"copy_ptr1" = call i8* @"strcpy"(i8* %"concat_ptr", i8* %"str_ptr1")
  %"offset_ptr2" = getelementptr i8, i8* %"concat_ptr", i32 %"len1"
  %"copy_ptr1.1" = call i8* @"strcpy"(i8* %"offset_ptr2", i8* %"str_ptr2")
  store i8* %"concat_ptr", i8** %"x"
  ret i32 0
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
@"__str_2" = internal constant [3 x i8] c"hi\00"
@"__str_3" = internal constant [4 x i8] c"yes\00"