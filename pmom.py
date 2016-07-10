try:
    import markdown
    formatter = markdown.markdown
except ImportError:
    formatter = lambda s: "".join("<p>" + p + "</p>" for p in s.splitlines() if p)

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

def render(tree, stylesheet, title="(untitled)"):
    return """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>{1}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
{2}
</style>
</head>
<body>
{0}
</body>
</html>""".format(to_html(tree), title, stylesheet.read())

def print_tree(tree, level=0):
    if "title" in tree:
        print(("  " * (level-1)) + "* " + tree["title"])
    if tree["text"].strip():
        print(("  " * level) + tree["text"].strip())
    for child in tree["children"]:
        print_tree(child, level+1)

def flatten(tree, level=0):
    out = ""
    out += "*" * level
    if out: out += " "
    if "state" in tree and tree["state"]:
        out += tree["state"] + " "
    if "title" in tree:
        out += tree["title"]
    if "tags" in tree and tree["tags"]:
        out += " :{0}:".format(":".join(tree["tags"]))
    if tree["text"]:
        out += "\n" + tree["text"]
    out += "\n"
    for child in tree["children"]:
        out += flatten(child, level+1)
    return out

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    with open(filename, "r") as file:
        with open("style.css", "r") as stylesheet:
            print(render(make_tree(parse(file.read())),
                stylesheet=stylesheet))