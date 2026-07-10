import argparse
from . import __version__
from .i18n import msg, category_name
from .problems import load_problems, find_problem
from .progress import is_done, mark_done, load_progress, start_problem, elapsed_time, total_elapsed_time
from .runner import run_problem, format_value
from .templates import create_solution


def title(problem, lang):
    return problem["title_zh"] if lang == "zh" else problem["title_en"]


def print_problem(problem, lang):
    print(f"{msg(lang, 'id')}: {problem['id']}")
    print(f"{msg(lang, 'title')}: {title(problem, lang)}")
    print(f"{msg(lang, 'difficulty')}: {problem['difficulty']}")
    cats = ", ".join(category_name(lang, c) for c in problem["categories"])
    print(f"{msg(lang, 'categories')}: {cats}")
    if problem.get("url"):
        print(f"{msg(lang, 'url')}: {problem['url']}")
    fn = problem["function"]
    params = ", ".join(f"{name}: {typ}" for name, typ in fn["params"])
    print(f"Python: Solution.{fn['name']}({params}) -> {fn['return']}")
    for item in problem.get("examples", []):
        print(f"input: {format_value(item['input'])}")
        print(f"output: {format_value(item['output'])}")


def command_list(args):
    problems = load_problems()
    if args.category:
        problems = [p for p in problems if args.category in p["categories"]]
    if args.difficulty:
        problems = [p for p in problems if p["difficulty"] == args.difficulty]
    print(f"{msg(args.lang, 'id'):>3}  {msg(args.lang, 'difficulty'):<6}  {msg(args.lang, 'status'):<8}  {msg(args.lang, 'title')}")
    for problem in problems:
        status = msg(args.lang, "done" if is_done(problem["id"]) else "todo")
        print(f"{problem['id']:>3}  {problem['difficulty']:<6}  {status:<8}  {title(problem, args.lang)}")


def command_show(args):
    if args.id is not None:
        problem = find_problem(args.id)
        if not problem:
            print(msg(args.lang, "not_found"))
            return
        print_problem(problem, args.lang)
    elif args.category:
        problems = load_problems()
        matches = [p for p in problems if args.category in p["categories"]]
        if not matches:
            print(msg(args.lang, "no_problems_found", category=args.category))
            return
        for i, problem in enumerate(matches):
            if i > 0:
                print()
            print_problem(problem, args.lang)
    else:
        print(msg(args.lang, "specify_id_or_category"))


def command_new(args):
    problem = find_problem(args.id)
    if not problem:
        print(msg(args.lang, "not_found"))
        return
    path, created = create_solution(problem)
    print(f"{msg(args.lang, 'created' if created else 'exists')}: {path}")


def command_test(args):
    problem = find_problem(args.id)
    if not problem:
        print(msg(args.lang, "not_found"))
        return
    ok, results = run_problem(problem, args.case)
    for result in results:
        if "error" in result:
            print(result["error"])
            continue
        print(f"{msg(args.lang, 'case')} {result['index']}: {msg(args.lang, 'passed' if result['passed'] else 'failed')}")
        if not result["passed"]:
            print(f"{msg(args.lang, 'input')}: {format_value(result['input'])}")
            print(f"{msg(args.lang, 'expected')}: {format_value(result['expected'])}")
            print(f"{msg(args.lang, 'actual')}: {format_value(result['actual'])}")
    print(msg(args.lang, "passed" if ok else "failed"))


def command_start(args):
    problem = find_problem(args.id)
    if not problem:
        print(msg(args.lang, "not_found"))
        return
    start_problem(args.id)
    print(f"{msg(args.lang, 'started')}: {args.id}")


def command_done(args):
    if not find_problem(args.id):
        print(msg(args.lang, "not_found"))
        return
    mark_done(args.id)
    elapsed = elapsed_time(args.id)
    if elapsed:
        print(f"{msg(args.lang, 'marked_done')}: {args.id}  ({msg(args.lang, 'elapsed')}: {elapsed})")
    else:
        print(f"{msg(args.lang, 'marked_done')}: {args.id}")


def command_stats(args):
    total = len(load_problems())
    completed = len(load_progress().get("done", {}))
    print(f"{msg(args.lang, 'total')}: {total}")
    print(f"{msg(args.lang, 'completed')}: {completed}")
    time_str = total_elapsed_time()
    if time_str != "0s":
        print(f"{msg(args.lang, 'total_time')}: {time_str}")


def add_lang(parser):
    parser.add_argument("--lang", choices=["en", "zh"], default="en")


def build_parser():
    parser = argparse.ArgumentParser(description=msg("en", "usage"))
    parser.add_argument(
        "--version", action="version",
        version=f"lc-simulator {__version__}"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("list")
    add_lang(p)
    p.add_argument("--category")
    p.add_argument("--difficulty", choices=["easy", "medium", "hard"])
    p.set_defaults(func=command_list)
    p = sub.add_parser("show")
    add_lang(p)
    p.add_argument("id", type=int, nargs="?", help="problem ID")
    p.add_argument("--category", help="filter by category")
    p.set_defaults(func=command_show)
    p = sub.add_parser("new")
    add_lang(p)
    p.add_argument("id", type=int)
    p.set_defaults(func=command_new)
    p = sub.add_parser("start")
    add_lang(p)
    p.add_argument("id", type=int)
    p.set_defaults(func=command_start)
    p = sub.add_parser("test")
    add_lang(p)
    p.add_argument("id", type=int)
    p.add_argument("--case", type=int, metavar="N", help="run only the N-th test case (1-based)")
    p.set_defaults(func=command_test)
    p = sub.add_parser("done")
    add_lang(p)
    p.add_argument("id", type=int)
    p.set_defaults(func=command_done)
    p = sub.add_parser("stats")
    add_lang(p)
    p.set_defaults(func=command_stats)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
