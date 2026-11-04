"""Parse the compiled manuscript's .aux file for verified section/table/figure numbers, pages and line labels."""
import re


def parse_aux(path):
    out = {}
    for line in open(path, encoding="utf-8", errors="ignore"):
        m = re.match(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}\{([^}]*)\}", line)
        if m:
            out[m.group(1)] = (m.group(2), m.group(3))
    return out


class Loc:
    def __init__(self, aux):
        self.a = parse_aux(aux)

    def line(self, key):
        ln, pg = self.a[key]
        return f"p. {pg}, line {ln}"

    def sec(self, key):
        n, pg = self.a[key]
        return f"Section {n} (p. {pg})"

    def tab(self, key):
        n, pg = self.a[key]
        return f"Table {n} (p. {pg})"

    def fig(self, key):
        n, pg = self.a[key]
        return f"Figure {n} (p. {pg})"

    def num(self, key):
        return self.a[key][0]
