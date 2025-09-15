# utils.py
# Small helper functions for two's complement and bit ops.

def mask(bits: int) -> int:
    return (1 << bits) - 1

def int_to_twos(value: int, bits: int) -> int:
    """
    Convert a signed integer to its unsigned two's complement representation with `bits` bits.
    """
    return value & mask(bits)

def twos_to_int(uvalue: int, bits: int) -> int:
    """
    Interpret an unsigned integer as a signed two's complement with `bits` bits.
    """
    sign_bit = 1 << (bits - 1)
    if uvalue & sign_bit:
        # negative
        return uvalue - (1 << bits)
    else:
        return uvalue

def add_bits(a: int, b: int, bits: int) -> int:
    """
    Add two 'bits'-wide unsigned registers and return masked result.
    """
    return (a + b) & mask(bits)

def sub_bits(a: int, b: int, bits: int) -> int:
    """
    Compute a - b in 'bits' wide two's complement representation (returns masked result).
    """
    return (a + ((~b + 1) & mask(bits))) & mask(bits)

def arithmetic_right_shift_AQ(A: int, Q: int, Q_1: int, n: int):
    """
    Perform arithmetic right shift on the combined A (n bits), Q (n bits), Q_1 (1 bit).
    Returns (A_new, Q_new, Q_1_new).
    A is treated as signed (so sign bit replicated).
    The shifting rule:
      - Q_1 <- least significant bit of Q (old)
      - Q <- (Q >> 1) | ((A & 1) << (n-1))
      - A <- arithmetic right shift of A (sign-extend)
    All results masked to n bits where appropriate.
    """
    m = (1 << n) - 1
    # new Q_1 is old LSB of Q
    new_Q_1 = Q & 1

    # Q's new value gets A's LSB into its MSB position
    new_Q = ((Q >> 1) | ((A & 1) << (n - 1))) & m

    # arithmetic right shift for A
    sign_mask = 1 << (n - 1)
    if A & sign_mask:
        # negative: shift and set top bit
        new_A = ((A >> 1) | sign_mask) & m
    else:
        new_A = (A >> 1) & m

    return new_A, new_Q, new_Q_1

