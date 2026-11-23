"""
CodeGuard's similarity engine.

Two independent signals are computed and blended:

1. Token similarity (works for ANY language):
   - Strip comments/whitespace, split into tokens, normalize identifiers.
   - Compare the two token-sets with Jaccard similarity.
   - Catches copy-pasted code, including with cosmetic edits.

2. Structural similarity (Python only, via the `ast` module):
   - Parse each submission into an Abstract Syntax Tree.
   - Reduce the tree to a sequence of node-type labels (ignoring names,
     literals, comments, formatting).
   - Compare the two label-sequences with a ratio based on the longest
     common subsequence (via difflib.SequenceMatcher).
   - Catches submissions that were restructured / renamed to dodge a
     plain text or token diff, because the *shape* of the logic is
     still the same.

combined_score is a weighted blend, biased toward structure when it is
available (Python), and falls back to token-only for other languages.
"""

import ast
import difflib
import keyword
import re
import tokenize
import io

TOKEN_WEIGHT_WHEN_NO_STRUCTURE = 1.0
TOKEN_WEIGHT_WHEN_STRUCTURE = 0.4
STRUCTURE_WEIGHT = 0.6

_IDENTIFIER_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def _normalize_tokens(code: str) -> set:
    """
    Tokenize source code, drop comments/whitespace, and normalize every
    user-defined identifier to a generic placeholder so renaming a
    variable doesn't change the token signature. Keywords, operators,
    and literals are kept as-is since they carry real signal.
    """
    tokens = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(code).readline):
            tok_type, tok_string, *_ = tok
            if tok_type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
                             tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING,
                             tokenize.ENDMARKER):
                continue
            if tok_type == tokenize.NAME and not keyword.iskeyword(tok_string):
                tokens.append('ID')  # normalize variable/function names
            else:
                tokens.append(tok_string.strip())
    except (tokenize.TokenizeError, IndentationError, SyntaxError):
        # Non-Python or malformed code: fall back to a crude whitespace split
        cleaned = re.sub(r'//.*|#.*|/\*.*?\*/', '', code, flags=re.S)
        for word in cleaned.split():
            tokens.append('ID' if _IDENTIFIER_RE.match(word) else word)

    return set(t for t in tokens if t)


def token_similarity(code_a: str, code_b: str) -> float:
    """Jaccard similarity over normalized token sets, as a percentage."""
    set_a, set_b = _normalize_tokens(code_a), _normalize_tokens(code_b)
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return 100.0 * intersection / union if union else 0.0


def _ast_node_sequence(code: str):
    """Flatten a parsed AST into a list of node type names, in traversal order."""
    tree = ast.parse(code)
    return [type(node).__name__ for node in ast.walk(tree)]


def structure_similarity(code_a: str, code_b: str):
    """
    AST-shape similarity, as a percentage. Returns None if either
    submission fails to parse as Python (e.g. wrong language, or
    deliberately obfuscated/invalid code).
    """
    try:
        seq_a = _ast_node_sequence(code_a)
        seq_b = _ast_node_sequence(code_b)
    except (SyntaxError, ValueError):
        return None

    if not seq_a or not seq_b:
        return None

    matcher = difflib.SequenceMatcher(a=seq_a, b=seq_b)
    return round(matcher.ratio() * 100, 2)


def compare_submissions(code_a: str, code_b: str) -> dict:
    """
    Returns a dict with token_similarity, structure_similarity
    (possibly None) and combined_score, all as percentages 0-100.
    """
    t_sim = round(token_similarity(code_a, code_b), 2)
    s_sim = structure_similarity(code_a, code_b)

    if s_sim is None:
        combined = t_sim * TOKEN_WEIGHT_WHEN_NO_STRUCTURE
    else:
        combined = (t_sim * TOKEN_WEIGHT_WHEN_STRUCTURE) + (s_sim * STRUCTURE_WEIGHT)

    return {
        'token_similarity': t_sim,
        'structure_similarity': s_sim,
        'combined_score': round(combined, 2),
    }
