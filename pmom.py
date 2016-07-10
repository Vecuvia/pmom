try:
    import markdown
    formatter = markdown.markdown
except ImportError:
    formatter = lambda s: "".join("<p>" + p + "</p>" for p in s.splitlines() if p)

test = """pmo-m

(poor man's org-mode)

* TODO Some text
This is the body text.

** Second level title
It could be used as a simple outliner

** TODO Text :tag:tag:

* First level 1

** Second level 2

* First level 2

"""

STATES = ["TODO", "DONE"]

def count(char, line):
    occ = 0
    for c in line:
        if c == char:
            occ += 1
        else:
            break
    return occ

def parse_header(line):
    level = count("*", line)
    tokens = line[level:].strip().split(" ")
    state = ""
    if tokens[0] in STATES:
        state = tokens.pop(0)
    tags = []
    if tokens[-1].startswith(":") and tokens[-1].endswith(":"):
        tags = tokens.pop(-1)[1:-1].split(":")
    title = " ".join(tokens)
    return {
        "level": level,
        "title": title,
        "state": state,
        "tags": tags,
        "text": "",
        "children": []
    }

def parse(text):
    out = [{"level": 0, "text": "", "children": []}]
    for line in text.splitlines():
        if line.startswith("*"):
            out.append(parse_header(line))
        else:
            out[-1]["text"] += line + "\n"
    return out

def make_tree(iterable, item=0):
    tree = iterable[item]
    i = item + 1
    while i < len(iterable):
        if iterable[i]["level"] == tree["level"] + 1:
            tree["children"].append(make_tree(iterable, i))
        elif iterable[i]["level"] <= tree["level"]:
            break
        i += 1
    return tree

def to_html(tree):
    out = ""
    if "state" in tree and tree["state"]:
        out += "<strong class=\"{0}\">{0}</strong> ".format(tree["state"])
    if "title" in tree:
        out += "<strong>{0}</strong>".format(tree["title"])
    if "tags" in tree:
        for tag in tree["tags"]:
            out += " <span class=\"tag\">#{0}</span>".format(tag)
    if tree["text"]:
        out += "{0}".format(formatter(tree["text"]))
    if tree["children"]:
        out += "<ul>"
        for child in tree["children"]:
            out += "<li>{0}</li>".format(to_html(child))
        out += "</ul>"
    return out

def print_tree(tree, level=0):
    if "title" in tree:
        print(("  " * (level-1)) + "* " + tree["title"])
    if tree["text"].strip():
        print(("  " * level) + tree["text"].strip())
    for child in tree["children"]:
        print_tree(child, level+1)

from pprint import pprint
tree = make_tree(parse(test))
#pprint(tree)
#print_tree(tree)
print(to_html(tree))