import tokenize
with open("check.py", "rb") as f:
    for token in tokenize.tokenize(f.readline):
        if token.type == tokenize.STRING:
             print(f"STRING: {token.start} -> {token.end}")
        elif token.string == '(':
             print(f"OPEN (: {token.start}")
        elif token.string == ')':
             print(f"CLOSE ): {token.start}")
