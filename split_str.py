def split_str(s, n):
    "split string by its length"
    length = len(s)
    return [s[i:i+n] for i in range(0, length, n)]