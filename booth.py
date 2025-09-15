# booth.py
# Booth algorithm implementation using masked registers A, Q, Q-1.

from utils import int_to_twos, twos_to_int, add_bits, sub_bits, arithmetic_right_shift_AQ, mask

class BoothSimulator:
    def __init__(self, multiplicand: int, multiplier: int, bits: int = 8):
        assert bits >= 4, "Choose at least 4 bits for demonstration."
        self.n = bits
        self.mask = mask(bits)
        # store signed inputs for final display
        self.M_signed = multiplicand
        self.Q_signed = multiplier

        # registers stored as unsigned two's complement patterns
        self.M = int_to_twos(multiplicand, bits)   # multiplicand register (n bits)
        self.A = 0                                 # A register (n bits)
        self.Q = int_to_twos(multiplier, bits)     # Q register (n bits)
        self.Q_1 = 0                               # Q-1 bit (0 or 1)
        self.step_count = 0
        self.log = []  # store steps as dicts for visualization

    def step(self):
        """
        Perform single Booth iteration and return a dict describing the action.
        """
        if self.step_count >= self.n:
            return {"finished": True}
        q0 = self.Q & 1
        pair = (q0, self.Q_1)
        action = "NONE"
        # Determine action
        if pair == (1, 0):
            # A = A - M
            oldA = self.A
            self.A = sub_bits(self.A, self.M, self.n)
            action = "SUB (A = A - M)"
        elif pair == (0, 1):
            # A = A + M
            oldA = self.A
            self.A = add_bits(self.A, self.M, self.n)
            action = "ADD (A = A + M)"
        else:
            action = "NONE"

        # perform arithmetic right shift on A,Q,Q_1
        old_A, old_Q, old_Q1 = self.A, self.Q, self.Q_1
        self.A, self.Q, self.Q_1 = arithmetic_right_shift_AQ(self.A, self.Q, self.Q_1, self.n)
        self.step_count += 1

        # record step snapshot
        step_info = {
            "step": self.step_count,
            "action": action,
            "A": self.A,
            "Q": self.Q,
            "Q_1": self.Q_1,
            "M": self.M,
            "A_signed": twos_to_int(self.A, self.n),
            "Q_signed": twos_to_int(self.Q, self.n),
            "combined_product_unsigned": ((self.A << self.n) | self.Q) & ((1 << (2 * self.n)) - 1),
            "combined_product_signed": twos_to_int(((self.A << self.n) | self.Q) & ((1 << (2 * self.n)) - 1), 2 * self.n)
        }
        self.log.append(step_info)
        return step_info

    def run(self):
        """
        Run until completion (n steps). Returns the final product info dict.
        """
        while self.step_count < self.n:
            self.step()
        product_unsigned = ((self.A << self.n) | self.Q) & ((1 << (2 * self.n)) - 1)
        product_signed = twos_to_int(product_unsigned, 2 * self.n)
        return {
            "A": self.A,
            "Q": self.Q,
            "Q_1": self.Q_1,
            "product_unsigned": product_unsigned,
            "product_signed": product_signed,
            "steps": self.log
        }

    def reset(self, multiplicand: int = None, multiplier: int = None, bits: int = None):
        """
        Reset simulator (optionally with new inputs).
        """
        if multiplicand is not None:
            self.M_signed = multiplicand
        if multiplier is not None:
            self.Q_signed = multiplier
        if bits is not None:
            self.n = bits
            self.mask = mask(bits)
        self.M = int_to_twos(self.M_signed, self.n)
        self.A = 0
        self.Q = int_to_twos(self.Q_signed, self.n)
        self.Q_1 = 0
        self.step_count = 0
        self.log = []

