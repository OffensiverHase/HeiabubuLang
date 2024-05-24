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

declare i32 @"strcmp"(i8* %".1", i8* %".2")

declare i32 @"getchar"()

define i32 @"load_main"()
{
load_main_entry:
  %"a" = alloca double
  %"b" = alloca double
  %"c" = alloca double
  %"c_str" = alloca i8*
  %"x" = alloca i1
  %"y" = alloca i1
  %"c_str.1" = alloca i8*
  store double 0x404b800000000000, double* %"a"
  store double 0x4004000000000000, double* %"b"
  %"a.1" = load double, double* %"a"
  %"b.1" = load double, double* %"b"
  %"div" = fdiv double %"a.1", %"b.1"
  store double %"div", double* %"c"
  %"str_bitcast" = bitcast [3 x i8]* @"__str_0" to i8*
  %"c.1" = load double, double* %"c"
  store i8* %"str_bitcast", i8** %"c_str"
  %"c_str_to_ptr" = bitcast [3 x i8]* @"__str_0" to i8*
  %"printf.ret" = call i32 (i8*, ...) @"printf"(i8* %"c_str_to_ptr", double %"c.1")
  %"true" = load i1, i1* @"true"
  store i1 %"true", i1* %"x"
  %"x.1" = load i1, i1* %"x"
  %".7" = xor i1 %"x.1", -1
  store i1 %".7", i1* %"y"
  %"str_bitcast.1" = bitcast [3 x i8]* @"__str_1" to i8*
  %"y.1" = load i1, i1* %"y"
  store i8* %"str_bitcast.1", i8** %"c_str.1"
  %"c_str_to_ptr.1" = bitcast [3 x i8]* @"__str_1" to i8*
  %"printf.ret.1" = call i32 (i8*, ...) @"printf"(i8* %"c_str_to_ptr.1", i1 %"y.1")
  ret i32 0
}

@"__str_0" = internal constant [3 x i8] c"%z\00"
@"__str_1" = internal constant [3 x i8] c"%i\00"