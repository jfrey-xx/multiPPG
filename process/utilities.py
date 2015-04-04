
def nextPow2(value):
    """
    Return the power of 2 immediately superior to this value
    """
    p = 1
    while p < value:
        p <<= 1 # shift one bit until we're good
    return p
