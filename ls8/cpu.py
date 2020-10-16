import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.running = False
        self.sp = 7  # our stack pointer starts at the top of a 0-7 index
        self.fl = 0b00000000  # all flags set to false on initialization
        self.reg[self.sp] = 0xf4  # initialize stack pointer to RAM address f4

    def call_stack(self, func):
        branch_table = {
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b10100010: self.MULT,
            0b00000001: self.HLT,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b01010000: self.CALL,
            0b00010001: self.RET
        }
        if func in branch_table:
            branch_table[func]()
        else:
            print('invalid function')
            sys.exit(1)

    def LDI(self):  # converts value to int
        reg_num = self.ram_read(self.pc+1)
        value = self.ram_read(self.pc+2)
        self.reg[reg_num] = value
        self.pc += 3

    def PRN(self):  # prints to console
        reg_num = self.ram_read(self.pc+1)
        print(self.reg[reg_num])
        self.pc += 2

    def HLT(self):
        self.running = False
        self.pc += 1

    def MULT(self):
        self.alu('MULT', self.pc+1, self.pc+2)
        self.pc += 3

    def PUSH(self, value=None):
        # decrement SP
        self.sp -= 1
        if not value:
            value = self.reg[self.ram_read(self.pc + 1)]
        self.ram_write(value, self.reg[self.sp])
        self.pc += 2

    def POP(self):
        value = self.ram[self.sp]
        # go to next in ram
        self.reg[self.ram[self.pc + 1]] = value
        # increment sp
        self.sp += 1
        self.pc += 2

    def CALL(self):
        new_pc = self.reg[self.ram_read(self.pc + 1)]
        self.PUSH(self.pc + 2)
        self.pc = new_pc

    def RET(self):
        self.pc = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    def load(self, filename):
        """Load a program into memory."""
        # print(self.ram)
        address = 0
        
        with open(f'examples/{filename}') as f:
            for line in f:
                line = line.split('#')[0].strip()
                if line == "":
                    continue
                value = int(line, base = 2)
                self.ram[address] = value
                address += 1
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MULT":
            self.reg[self.ram[reg_a]] *= self.reg[self.ram[reg_b]]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.fl,
            self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            ir = self.ram[self.pc]
            self.call_stack(ir)