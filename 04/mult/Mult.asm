
//// Replace this comment with your code.
@R0    // r0
D=M
@i
M=D    // i = r0
@R1    
D=M
@j
M=D    // j=r1
@R2    // r2 -> answer box
M=0
(LOOP)
@j
D=M
@END
D;JLE  // j <= 0 end
@j
M=D-1  // j=j-1
@i
D=M // i= d
@R2
M=M+D  // sum = sum + i
@LOOP
0;JMP
(END)
@END
0;JMP
