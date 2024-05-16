; ModuleID = '<string>'
source_filename = "<string>"
target triple = "x86_64-unknown-linux-gnu"

%A = type { i32 }

@true = local_unnamed_addr constant i1 true
@false = local_unnamed_addr constant i1 false
@__str_0 = internal constant [5 x i8] c"%i\0A\00\00"
@__str_1 = internal constant [5 x i8] c"%i\0A\00\00"

; Function Attrs: nofree nounwind
declare noundef i32 @printf(i8* nocapture noundef readonly, ...) local_unnamed_addr #0

; Function Attrs: mustprogress nofree norecurse nosync nounwind readnone willreturn
define i32 @load_main() local_unnamed_addr #1 {
load_main_entry:
  ret i32 0
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind readnone willreturn
define i32 @nice(%A* nocapture readnone %.1) local_unnamed_addr #1 {
nice_entry:
  ret i32 69
}

; Function Attrs: nofree nounwind
define void @hell_yeah(%A* nocapture readonly %.1) local_unnamed_addr #0 {
hell_yeah_entry:
  %printf.ret = tail call i32 (i8*, ...) @printf(i8* nonnull dereferenceable(1) getelementptr inbounds ([5 x i8], [5 x i8]* @__str_0, i64 0, i64 0), i32 69)
  %A.x_ptr = getelementptr %A, %A* %.1, i64 0, i32 0
  %A.x = load i32, i32* %A.x_ptr, align 4
  %printf.ret.1 = tail call i32 (i8*, ...) @printf(i8* nonnull dereferenceable(1) getelementptr inbounds ([5 x i8], [5 x i8]* @__str_1, i64 0, i64 0), i32 %A.x)
  ret void
}

; Function Attrs: nofree nounwind
define void @main() local_unnamed_addr #0 {
main_entry:
  %A = alloca %A, align 8
  %A.x_ptr = getelementptr inbounds %A, %A* %A, i64 0, i32 0
  store i32 420, i32* %A.x_ptr, align 8
  call void @hell_yeah(%A* nonnull %A)
  ret void
}

attributes #0 = { nofree nounwind }
attributes #1 = { mustprogress nofree norecurse nosync nounwind readnone willreturn }
