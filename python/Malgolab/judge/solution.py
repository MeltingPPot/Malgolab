"""Solution scaffolding: generates boilerplate code and notes from templates."""

from datetime import date

from ..paths import templates_dir, solutions_dir, ensure_dir


def _default_template():
    return (
        "// $TITLE$\n"
        "// OJ: $OJ$, ID: $PID$\n"
        "// Date: $DATE$\n"
        "#include <bits/stdc++.h>\n"
        "using namespace std;\n\n"
        "int main() {\n"
        "    // Your code here\n"
        "    return 0;\n"
        "}\n"
    )


def ensure_templates_exist():
    """Create the templates directory and default.cpp if missing."""
    tdir = templates_dir()
    ensure_dir(tdir)
    default = tdir / 'default.cpp'
    if not default.exists():
        default.write_text(_default_template())


def generate_solution(oj, pid, template_name='default', title=''):
    """Create sol.cpp and notes.md for a problem, returning the target dir.

    Placeholders $OJ$, $PID$, $TITLE$, $DATE$ are substituted.
    """
    tdir = templates_dir()
    template_file = tdir / f'{template_name}.cpp'
    if not template_file.exists():
        template_file = tdir / 'default.cpp'
    if not template_file.exists():
        raise FileNotFoundError(
            "No template found. Create templates/default.cpp first.")

    content = template_file.read_text()
    content = content.replace('$OJ$', oj)
    content = content.replace('$PID$', pid)
    content = content.replace('$TITLE$', title)
    content = content.replace('$DATE$', date.today().strftime('%Y-%m-%d'))

    sdir = solutions_dir()
    ensure_dir(sdir)
    target_dir = sdir / oj / pid
    target_dir.mkdir(parents=True, exist_ok=True)

    sol_file = target_dir / 'sol.cpp'
    if not sol_file.exists():
        sol_file.write_text(content)

    note_file = target_dir / 'notes.md'
    if not note_file.exists():
        note_file.write_text(f"# {oj} {pid} - {title}\n")

    return target_dir
