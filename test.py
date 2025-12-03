import tokenize
import token
from io import StringIO

def remove_comments_and_docstrings(code):

    tokens = tokenize.generate_tokens(StringIO(code).readline)
    result = []
    prev_tok_type = None

    for tok_type, tok_string, start, end, line in tokens:
        # Remove line comments
        if tok_type == tokenize.COMMENT:
            continue

        # Remove docstrings (string tokens right after a def, class, or at top-level)
        if tok_type == tokenize.STRING:
            if prev_tok_type in {tokenize.INDENT, tokenize.DEDENT, tokenize.NEWLINE, None}:
                # This is likely a standalone docstring → skip it
                if tok_string.startswith(("'''", '"""')):
                    prev_tok_type = tok_type
                    continue

        result.append((tok_type, tok_string, start, end, line))
        prev_tok_type = tok_type

    return tokenize.untokenize(result)

def clean_file(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        code = f.read()

    cleaned = remove_comments_and_docstrings(code)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(cleaned)

if __name__ == "__main__":
    clean_file("main.py", "main_no_comments.py")
