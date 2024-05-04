; ModuleID = 'test.c'
source_filename = "test.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

; Function Attrs: noinline nounwind optnone
define dso_local i32 @main() #0 {
entry:
  %retval = alloca i32, align 4
  %one = alloca i32, align 4
  %a = alloca [5 x i32], align 16
  store i32 0, i32* %retval, align 4
  store i32 1, i32* %one, align 4
  %arrayinit.begin = getelementptr inbounds [5 x i32], [5 x i32]* %a, i64 0, i64 0
  %0 = load i32, i32* %one, align 4
  store i32 %0, i32* %arrayinit.begin, align 4
  %arrayinit.element = getelementptr inbounds i32, i32* %arrayinit.begin, i64 1
  store i32 2, i32* %arrayinit.element, align 4
  %arrayinit.element1 = getelementptr inbounds i32, i32* %arrayinit.element, i64 1
  store i32 3, i32* %arrayinit.element1, align 4
  %arrayinit.element2 = getelementptr inbounds i32, i32* %arrayinit.element1, i64 1
  store i32 4, i32* %arrayinit.element2, align 4
  %arrayinit.element3 = getelementptr inbounds i32, i32* %arrayinit.element2, i64 1
  store i32 5, i32* %arrayinit.element3, align 4
  %arrayidx = getelementptr inbounds [5 x i32], [5 x i32]* %a, i64 0, i64 10
  %1 = load i32, i32* %arrayidx, align 8
  ret i32 %1
}

attributes #0 = { noinline nounwind optnone "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-features"="+cx8,+mmx,+sse,+sse2,+x87" }

!llvm.module.flags = !{!0}
!llvm.ident = !{!1}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{!"Ubuntu clang version 14.0.0-1ubuntu1.1"}
