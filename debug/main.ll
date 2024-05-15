; ModuleID = "main_main"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

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
  ret i32 0
}

define i32* @"lst"()
{
lst_entry:
  %"list_ptr" = alloca [3 x i32]
  %"array.0" = getelementptr [3 x i32], [3 x i32]* %"list_ptr", i32 0, i32 0
  store i32 1, i32* %"array.0"
  %"array.0.1" = getelementptr i32, i32* %"array.0", i32 1
  store i32 2, i32* %"array.0.1"
  %"array.1" = getelementptr i32, i32* %"array.0.1", i32 1
  store i32 3, i32* %"array.1"
  %"ret_temp" = getelementptr [3 x i32], [3 x i32]* %"list_ptr", i32 0, i32 0
  ret i32* %"ret_temp"
}

define void @"main"()
{
main_entry:
  %"a" = alloca i32*
  %"c_str" = alloca i8*
  %"lst.ret" = call i32* @"lst"()
  store i32* %"lst.ret", i32** %"a"
  %"str_bitcast" = bitcast [3 x i8]* @"__str_0" to i8*
  %"a.1" = load i32*, i32** %"a"
  %"list_element_ptr" = getelementptr i32, i32* %"a.1", i32 1
  %"list_element" = load i32, i32* %"list_element_ptr"
  store i8* %"str_bitcast", i8** %"c_str"
  %"c_str_to_ptr" = bitcast [3 x i8]* @"__str_0" to i8*
  %"printf.ret" = call i32 (i8*, ...) @"printf"(i8* %"c_str_to_ptr", i32 %"list_element")
  ret void
}

@"__str_0" = internal constant [3 x i8] c"%i\00"