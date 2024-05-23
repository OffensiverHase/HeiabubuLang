; ModuleID = '<string>'
source_filename = "<string>"
target triple = "x86_64-unknown-linux-gnu"

%C = type { i32 }

@true = local_unnamed_addr constant i1 true
@false = local_unnamed_addr constant i1 false
@__str_0 = internal constant [5 x i8] c"%i\0A\00\00"
@__str_1 = internal constant [3 x i8] c"%i\00"

; Function Attrs: nofree nounwind
declare noundef i32 @printf(i8* nocapture noundef readonly, ...) local_unnamed_addr #0

; Function Attrs: nofree nounwind
define i32 @load_main() local_unnamed_addr #0 {
load_main_entry:
  %C = alloca %C, align 8
  call void @"C:create.C*.i32"(%C* nonnull %C, i32 1)
  %C.num_ptr = getelementptr inbounds %C, %C* %C, i64 0, i32 0
  %C.num = load i32, i32* %C.num_ptr, align 8
  %printf.ret = tail call i32 (i8*, ...) @printf(i8* nonnull dereferenceable(1) getelementptr inbounds ([5 x i8], [5 x i8]* @__str_0, i64 0, i64 0), i32 %C.num)
  call void @"change.C*"(%C* nonnull %C)
  %C.num.1 = load i32, i32* %C.num_ptr, align 8
  %printf.ret.1 = tail call i32 (i8*, ...) @printf(i8* nonnull dereferenceable(1) getelementptr inbounds ([3 x i8], [3 x i8]* @__str_1, i64 0, i64 0), i32 %C.num.1)
  ret i32 0
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn writeonly
define void @"C:a.C*"(%C* nocapture writeonly %.1) local_unnamed_addr #1 {
"C:a.C*_entry":
  %C.num_ptr = getelementptr %C, %C* %.1, i64 0, i32 0
  store i32 10, i32* %C.num_ptr, align 4
  ret void
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn writeonly
define void @"C:create.C*.i32"(%C* nocapture writeonly %.1, i32 %.2) local_unnamed_addr #1 {
"C:create.C*.i32_entry":
  %C.num_ptr = getelementptr %C, %C* %.1, i64 0, i32 0
  store i32 %.2, i32* %C.num_ptr, align 4
  ret void
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn
define void @"change.C*"(%C* nocapture %.1) local_unnamed_addr #2 {
"change.C*_entry":
  %C.num_ptr = getelementptr %C, %C* %.1, i64 0, i32 0
  %C.num = load i32, i32* %C.num_ptr, align 4
  %add = add i32 %C.num, 1
  store i32 %add, i32* %C.num_ptr, align 4
  ret void
}

attributes #0 = { nofree nounwind }
attributes #1 = { mustprogress nofree norecurse nosync nounwind willreturn writeonly }
attributes #2 = { mustprogress nofree norecurse nosync nounwind willreturn }
