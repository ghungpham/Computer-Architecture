"""CPU functionality."""

import sys


##ADD INSTRUCTION TO REFER BY NAME COMMAND INSTEAD OF NUMERIC VALUE

HLT  = 0b00000001
LDI  = 0b10000010
PRN  = 0b01000111
MUL  = 0b10100010
ADD  = 0b10100000
PUSH = 0b01000101
POP  = 0b01000110

CALL = 0b01010000
RET  = 0b00010001

SP   = 7


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8

        self.reg[7] = 0xF4

         #R7 is reserved as the stack pointer (SP)
         #The SP points at the value at the top of the stack (most recently pushed), or at address `F4` if the stack is empty.

        ##PC: Program Counter, address of the currently executing instruction
        self.PC = 0
        ##IR: Instruction Register, contains a copy of the currently executing instruction
        self.IR = None
        ##MAR: Memory Address Register, holds the memory address we're reading or writing
        ##MDR: Memory Data Register, holds the value to write or the value just read
        ##self.branchtable = {LDI: self.handle_LDI, PRN : self.handle_PRN, MUL: self.handle_MUL}

    def load(self):
        """Load a program into memory."""
    
        try:
            with open(sys.argv[1], 'r') as f:
                #ignore all the #instructions and #blank line
                lines = [line for line in f.readlines() if not (line[0]=='#' or line[0]=='\n')]
                program = [int(line.split('#')[0].strip(), 2) for line in lines]
            address = 0

            for instruction in program:
                self.ram[address] = instruction
                address += 1

        
        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)


        


        # address = 0

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            #self.fl,
            #self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            address= self.PC
            command = self.ram[address]

            ##HALT COMMAND
            if command == HLT:
                print('HLT == EXIT')
                running = False

            ##LDI register immediate
            ##Set the value of a register to an integer.
            ##This instruction sets a specified register to a specified value.
            elif command == LDI:
                register = self.ram[self.PC + 1]
                integer = self.ram[self.PC + 2]
                print(f"LDI integer {integer} at reg {register}")
                self.reg[register] = integer
                self.PC += 3


            ##Print numeric value stored in the given register.
            elif command == PRN:
                register = self.ram[self.PC + 1]
                print(f'PRN: {self.reg[register]} at reg {register}')
                self.PC += 2

            elif command == ADD:
                reg_a = self.ram[self.PC + 1]
                reg_b = self.ram[self.PC + 2]
                result = self.alu("ADD", reg_a, reg_b)
                reg_a = result
                print(f'ADD')
                self.PC += 3

            elif command == MUL:
                reg_a = self.ram[self.PC + 1]
                reg_b = self.ram[self.PC + 2]
                result = self.alu("MUL", reg_a, reg_b)
                reg_a = result
                self.PC += 3

            elif command == PUSH:
                print('PUSH')
                register = self.ram[self.PC + 1]
                value = self.reg[register]
                
                ###1. Decrement the `SP`.
                self.reg[SP] -= 1
                ###2. Copy the value in the given register to the address pointed to by SP
                self.ram[self.reg[SP]] = value
                self.PC +=  2

            elif command == POP:
                print('POP')
                register = self.ram[self.PC + 1]
                value = self.ram[self.reg[SP]]
                self.reg[register] = value

                self.reg[SP] += 1
                self.PC += 2

            elif command == CALL:
                print('CALL')
                #push the return address to where we left off where subroutine/func finishes executing
                self.reg[SP] -= 1
                self.ram[self.reg[SP]] = self.PC + 2

                #the pc is set to the address stored in the given register
                register = self.ram[self.PC + 1]
                #we jump to that location in the RAM and execute the function
                self.PC = self.reg[register]

            elif command == RET:
                print('RET')
                #Return from subroutine/routine.
                self.PC = self.ram[self.reg[SP]]
                #Pop the value from the top of the stack and store it in the `PC`.
                self.reg[SP] += 1
                
                



            else:
                print(f"unknown instruction {command}")
                self.PC += 1

          



    def ram_read(self, address):
        return self.ram[address]
    
    def ram_write(self, address, value):
        self.ram[address] = value
        return self.ram[address]
    
