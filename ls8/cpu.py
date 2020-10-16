import sys

class CPU:
    """Main CPU class."""
    def __init__(self):
        """Construct a new CPU."""

        self.reg = [0] * 8  # init register
        self.ram = [0] * 256  # init ram
        self.PC = 0  # program counter register
        self.sp = 7 # stack pointer, reg[7] reserved for this
        self.reg[self.sp] = 0xf4 # initialze stack as empty per spec

        # branch table
        self.branchtable = {}
        self.branchtable[0b01000111] = self.PRN
        self.branchtable[0b10000010] = self.LDI
        self.branchtable[0b10100010] = self.MUL
        self.branchtable[0b01000101] = self.PUSH
        self.branchtable[0b01000110] = self.POP
        # sprint additions #############################################################################
        self.branchtable[0b10100111] = self.CMP # cmp for sprint - compares the values and sets flag?
        self.branchtable[0b01010100] = self.JMP # jumps pc to an address in register
        self.branchtable[0b01010101] = self.JEQ # if e flag is true + 1 - jump to that register
        self.branchtable[0b01010110] = self.JNE # if flag is clear false + 0 - jump to that register
    
        self.FL = [0] * 8   # equal flag ???

    # Load the ls8 files from here
    def load(self, filename):
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
     

    # ALU - arithmetic logic unit
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        if op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        if op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        if op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        
        if op == "CMP": #Added CMP for sprint 
            if self.reg[reg_a] == self.reg[reg_b]: # if reg list is equal 
                #flags equal to 
                self.FL[5] = 0
                self.FL[6] = 0
                self.FL[7] = 1
            elif self.reg[reg_a] < self.reg[reg_b]: # if less then 
                # flags equal too 
                self.FL[5] = 1 
                self.FL[6] = 0
                self.FL[7] = 0
            elif self.reg[reg_a] > self.reg[reg_b]: #if greater then
                #flags equal too
                self.FL[5] = 0
                self.FL[6] = 1
        else:
            raise Exception("Anthony say's pick another")


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')
        for i in range(8):
            print(" %02X" % self.reg[i], end='')
        print()

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def LDI(self): # sets specified register to a specified number
        self.reg[self.ram_read(self.PC+1)] = self.ram_read(self.PC+2)
        self.PC += 3

    def PRN(self):
        print(self.reg[self.ram_read(self.PC+1)]) # prints exact value
        self.PC += 2

    def MUL(self):
        self.reg[self.ram_read(
            self.PC+1)] = (self.reg[self.ram_read(self.PC+1)] * self.reg[self.ram_read(self.PC+2)]) # multipies values using alu
        self.PC += 3

    def PUSH(self):
        self.reg[self.sp] -= 1 # minus (decrement) Stack pointer
        reg_num = self.ram[self.PC + 1] # grab the next param
        value = self.reg[reg_num] # set the index of that param in register to value
        self.ram[self.reg[self.sp]] = value # copy the reg value into the ram
        self.PC += 2 # increment the counter by 2 to next command

    def POP(self):
        # removes from stack
        value = self.ram[self.reg[self.sp]]
        reg_num = self.ram[self.PC + 1]
        self.reg[reg_num] = value
        self.reg[self.sp] += 1
        self.PC += 2 # increment by 2 
        
        ########################################################################################################

    # Sprint functions
    def CMP(self): # compares values in two registers
        self.alu("CMP", self.ram[self.PC+1], self.ram[self.PC+2])
        self.PC += 3 # incrementing pc by 3

    def JMP(self):
        self.PC = self.reg[self.ram[self.PC + 1]] # jump to the address in the given register

    def JEQ(self):
        if self.FL[7] == 1: # if equal flag is true
            self.PC = self.reg[self.ram[self.PC + 1]] # jump to the address in the given reg
        else:
            self.PC += 2 #incrementing pc by 2

    def JNE(self):
        if self.FL[7] == 0: # if equals flags is false
            self.PC = self.reg[self.ram[self.PC + 1]] # jump to the address in the given register
        else:
            self.PC += 2 #incrementing pc by 2


###################################################################################################################
    def run(self):
        """Run the CPU."""

        # opcode commands
        HLT = 0b00000001
        CALL = 0b01010000
        RET = 0b00010001
    
        running = True # runs while running is True
        
        ## "KITE" helped a lot here
        
        while running: # for loop control 
            command = self.ram_read(self.PC) # grabs current command using PC
            if command == HLT:  # if the command is equal to halt
                running = False # stops the loop
            elif command == CALL: #if command is equal to call
                return_address = self.PC + 2 #setting return address to pc
                self.reg[self.sp] -= 1 # decremnting one from register
                self.ram[self.reg[self.sp]] = return_address # setting ram and stack pointer to the return address
                reg_num = self.ram[self.PC + 1] # initing register number to the ram 
                self.PC = self.reg[reg_num] # updating pc to the register num
            elif command == RET: # if command is equal then it pops the return address off of stack
                self.PC = self.ram[self.reg[self.sp]] #pc is updated to ram with register[stack pointer]
                self.reg[self.sp] += 1 #adds one to reg
            else: # otherwise runs the function 
                self.branchtable[command]() #from the responding command in the branch table 