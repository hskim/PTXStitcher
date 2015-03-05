; ModuleID = 'test.cl'
target datalayout = "e-i64:64-v16:16-v32:32-n16:32:64"
target triple = "nvptx64"

; Function Attrs: noinline nounwind
define void @vector_square(<4 x float> addrspace(1)* nocapture readonly %input, <4 x float> addrspace(1)* nocapture %output) #0 {
entry:
  %0 = tail call i32 @llvm.ptx.read.ctaid.x() #2
  %1 = tail call i32 @llvm.ptx.read.ntid.x() #2
  %mul.i = mul nsw i32 %1, %0
  %2 = tail call i32 @llvm.ptx.read.tid.x() #2
  %add.i = add nsw i32 %mul.i, %2
  %idxprom = sext i32 %add.i to i64
  %arrayidx = getelementptr inbounds <4 x float> addrspace(1)* %input, i64 %idxprom
  %3 = load <4 x float> addrspace(1)* %arrayidx, align 16, !tbaa !8
  %mul = fmul <4 x float> %3, %3
  %arrayidx4 = getelementptr inbounds <4 x float> addrspace(1)* %output, i64 %idxprom
  store <4 x float> %mul, <4 x float> addrspace(1)* %arrayidx4, align 16, !tbaa !8
  ret void
}

; Function Attrs: nounwind readnone
declare i32 @llvm.ptx.read.ctaid.x() #1

; Function Attrs: nounwind readnone
declare i32 @llvm.ptx.read.ntid.x() #1

; Function Attrs: nounwind readnone
declare i32 @llvm.ptx.read.tid.x() #1

attributes #0 = { noinline nounwind "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { nounwind readnone }
attributes #2 = { nounwind }

!opencl.kernels = !{!0}
!nvvm.annotations = !{!6}
!llvm.ident = !{!7}

!0 = !{void (<4 x float> addrspace(1)*, <4 x float> addrspace(1)*)* @vector_square, !1, !2, !3, !4, !5}
!1 = !{!"kernel_arg_addr_space", i32 1, i32 1}
!2 = !{!"kernel_arg_access_qual", !"none", !"none"}
!3 = !{!"kernel_arg_type", !"float4*", !"float4*"}
!4 = !{!"kernel_arg_base_type", !"float __attribute__((ext_vector_type(4)))*", !"float __attribute__((ext_vector_type(4)))*"}
!5 = !{!"kernel_arg_type_qual", !"", !""}
!6 = !{void (<4 x float> addrspace(1)*, <4 x float> addrspace(1)*)* @vector_square, !"kernel", i32 1}
!7 = !{!"clang version 3.7.0 (trunk)"}
!8 = !{!9, !9, i64 0}
!9 = !{!"omnipotent char", !10, i64 0}
!10 = !{!"Simple C/C++ TBAA"}
