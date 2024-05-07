// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen
// by writing 'black' in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen by writing
// 'white' in every pixel;
// the screen should remain fully clear as long as no key is pressed.

//// Replace this comment with your code.



@col
M=0

(SETUP)

@SCREEN
D=A
@0   // @0 == screen
M=D

@i      // i = 0
M=0

@FILL
0;JMP

(KEYBOARD)


@KBD
D=M
@BLACK
D;JGT    // Keyboard press paint it black
@WHITE
D;JEQ    // Else white

(BLACK)
@col
D=M
@KEYBOARD
D;JLT     // already black
@col
M=-1      // fill black

@SETUP
0;JMP

(WHITE)
@col
D=M
@KEYBOARD
D;JEQ    // screen is already white
@col
M=0      // fill white

@SETUP
0;JMP


(FILL)

@i
D=M
@8192      // screen ends at 8192
D=D-A
@KEYBOARD
D;JGT      // (if i-8192)>0 go to start

@col
D=M    // fill color

@0     // load screen
A=M    // GET ADDRESS
M=D    // PAINT

@i
D=M+1
M=D

@SCREEN
D=D+A   //NEW ADDRESS

@0
M=D // next pixel

@FILL
0;JMP

