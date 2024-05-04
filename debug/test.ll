; ModuleID = 'test.c'
source_filename = "test.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@__const.lst.ret = private unnamed_addr constant [3 x i32] [i32 1, i32 2, i32 3], align 4

; Function Attrs: noinline nounwind optnone
define dso_local i32* @lst() #0 {
entry:
  %ret = alloca [3 x i32], align 4
  %0 = bitcast [3 x i32]* %ret to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* align 4 %0, i8* align 4 bitcast ([3 x i32]* @__const.lst.ret to i8*), i64 12, i1 false)
  %arraydecay = getelementptr inbounds [3 x i32], [3 x i32]* %ret, i64 0, i64 0
  ret i32* %arraydecay
}

; Function Attrs: argmemonly nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #1

; Function Attrs: noinline nounwind optnone
define dso_local i32 @main() #0 {
entry:
  %retval = alloca i32, align 4
  %arr = alloca i32*, align 8
  store i32 0, i32* %retval, align 4
  %call = call i32* @lst()
  store i32* %call, i32** %arr, align 8
  %0 = load i32*, i32** %arr, align 8
  %arrayidx = getelementptr inbounds i32, i32* %0, i64 1
  %1 = load i32, i32* %arrayidx, align 4
  ret i32 0
}

attributes #0 = { noinline nounwind optnone "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-features"="+cx8,+mmx,+sse,+sse2,+x87" }
attributes #1 = { argmemonly nofree nounwind willreturn }

!llvm.module.flags = !{!0}
!llvm.ident = !{!1}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{!"Ubuntu clang version 14.0.0-1ubuntu1.1"}
