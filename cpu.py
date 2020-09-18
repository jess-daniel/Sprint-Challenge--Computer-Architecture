"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.running = True
        self.sp = 7
        self.flags = 0b00000000

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self, filename):
        """Load a program into memory."""

        try:
            address = 0
            with open(filename) as f:
                for line in f:
                    line = line.split("#")[0].strip()
                    if line == "":
                        continue
                    else:
                        self.ram[address] = int(line, 2)
                        address += 1
        except FileNotFoundError:
            print(f"{sys.argv[0]}: {filename} not found")

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "MOD":
            if self.reg[reg_b] == 0:
                raise Exception("Second value can't be 0")
            else:
                self.reg[reg_a] %= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

    def run(self):
        """Run the CPU."""
        HLT = 0b00000001
        LDI = 0b10000010
        PRN = 0b01000111
        MUL = 0b10100010
        PUSH = 0b01000101
        POP = 0b01000110
        CALL = 0b01010000
        RET = 0b00010001
        ADD = 0b10100000
        SUB = 0b10100001
        DIV = 0b10100011
        MOD = 0b10100100

        CMP = 0b10100111
        JMP = 0b01010100
        JEQ = 0b01010101
        JNE = 0b01010110

        while self.running:
            command = self.ram[self.pc]

            operand_a = self.ram[self.pc + 1]
            operand_b = self.ram[self.pc + 2]

            if command == PRN:
                print(self.reg[operand_a])
                self.pc += 2

            elif command == LDI:
                self.reg[operand_a] = operand_b
                self.pc += 3

            elif command == MUL:
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3

            elif command == HLT:
                self.running == False
                sys.exit(0)

            elif command == PUSH:
                self.sp -= 1
                val = self.reg[operand_a]
                self.ram[self.sp] = val
                self.pc += 2

            elif command == POP:
                val = self.ram[self.sp]
                self.reg[operand_a] = val
                self.sp += 1
                self.pc += 2

            elif command == CALL:
                return_address = self.pc + 2
                self.reg[self.sp] -= 1
                self.ram[self.reg[self.sp]] = return_address
                val = self.reg[operand_a]
                self.pc = val

            elif command == RET:
                return_address = self.ram[self.reg[self.sp]]
                self.reg[self.sp] += 1
                self.pc = return_address

            elif command == ADD:
                self.alu("ADD", operand_a, operand_b)
                self.pc += 3

            elif command == MOD:
                self.alu("MOD", operand_a, operand_b)
                self.pc += 3

            elif command == DIV:
                self.alu("DIV", operand_a, operand_b)
                self.pc += 3

            elif command == SUB:
                self.alu("SUB", operand_a, operand_b)
                self.pc += 3

            elif command == CMP:
                reg_a = self.reg[operand_a]
                reg_b = self.reg[operand_b]
                if reg_a == reg_b:
                    self.flags = 1
                else:
                    self.flags = 0
                self.pc += 3

            elif command == JMP:
                self.pc = self.reg[operand_a]

            elif command == JEQ:
                a = self.flags
                if a == 1:
                    self.pc = self.reg[operand_a]
                elif a == 0:
                    self.pc += 2

            elif command == JNE:
                a = self.flags
                if a == 0:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2

            else:
                print(f'{command} not found')
                sys.exit(1)
