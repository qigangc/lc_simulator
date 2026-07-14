import argparse
import datetime
import json
import os
from . import __version__
from .i18n import msg, category_name
from .paths import PROGRESS_FILE, SUBMISSIONS_FILE
from .problems import load_problems, find_problem
from .progress import is_done, mark_done, load_progress, start_problem, elapsed_time, total_elapsed_time, record_submission, load_submissions
from .runner import run_problem, format_value, run_custom_case
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
    
    if getattr(args, "input", None):
        ok, results = run_custom_case(problem, args.input)
        for result in results:
            if "error" in result:
                print(result["error"])
                continue
            print(f"{msg(args.lang, 'input')}: {format_value(result['input'])}")
            print(f"{msg(args.lang, 'actual')}: {format_value(result['actual'])}")
        if results and "error" not in results[0]:
            verdict = "Accepted" if ok else "Runtime Error"
            record_submission(args.id, verdict, 1, 1)
            if ok:
                print(f"[PASS] {msg(args.lang, 'verdict_accepted')}")
            else:
                print(f"[ERROR] {msg(args.lang, 'verdict_runtime_error')}")
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
    passed_count = sum(1 for r in results if r.get("passed"))
    total_count = len(results)
    has_error = any("error" in r for r in results)
    if has_error:
        verdict = "Runtime Error"
    elif ok:
        verdict = "Accepted"
    else:
        verdict = "Wrong Answer"
    record_submission(args.id, verdict, passed_count, total_count)

    if has_error:
        print(f"[ERROR] {msg(args.lang, 'verdict_runtime_error')}")
    elif ok:
        print(f"[PASS] {msg(args.lang, 'verdict_accepted')}")
    else:
        print(f"[FAIL] {msg(args.lang, 'verdict_wrong_answer')}")


def command_history(args):
    """Show submission history."""
    submissions = load_submissions()
    if args.yesterday:
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        submissions = [s for s in submissions if s["at"].startswith(yesterday)]
    if not submissions:
        print(msg(args.lang, "no_submissions"))
        return

    # Print header
    print(f"{'#':>3}  {'ID':>3}  {'Time':<20}  {'Verdict':<15}  {'Cases':<8}")
    print("-" * 55)

    for i, sub in enumerate(reversed(submissions[-20:]), 1):  # show last 20
        pid = sub["id"]
        at = sub["at"]
        verdict = sub["verdict"]
        cases = f"{sub['passed']}/{sub['total']}"
        print(f"{i:>3}  {pid:>3}  {at:<20}  {verdict:<15}  {cases:<8}")


def command_footprint(args):
    """Show yesterday's practice footprint."""
    submissions = load_submissions()
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    recent = [s for s in submissions if s["at"].startswith(yesterday)]

    if not recent:
        print(msg(args.lang, "no_footprint"))
        return

    problem_ids = sorted(set(s["id"] for s in recent))
    problems = load_problems()
    problem_map = {p["id"]: p for p in problems}

    print(f"\n{msg(args.lang, 'footprint_title')} ({yesterday})")
    print("=" * 50)

    total_tests = 0
    accepted_count = 0
    for s in recent:
        total_tests += 1
        if s["verdict"] == "Accepted":
            accepted_count += 1

    for pid in problem_ids:
        p = problem_map.get(pid)
        if p is None:
            continue
        name = p["title_en"] if args.lang == "en" else p["title_zh"]
        submissions_for_pid = [s for s in recent if s["id"] == pid]
        last = submissions_for_pid[-1]
        attempts = len(submissions_for_pid)
        verdict = last["verdict"]
        status = "[PASS]" if verdict == "Accepted" else "[FAIL]"
        print(f"  {status} #{pid} {name}  ({attempts} attempt{'s' if attempts > 1 else ''})")

    print("-" * 50)
    print(f"  {msg(args.lang, 'footprint_total')}: {total_tests} {msg(args.lang, 'footprint_submissions')}, {accepted_count} {msg(args.lang, 'footprint_accepted')}")
    print()


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


def command_reset(args):
    """Clear all practice history."""
    progress = load_progress()
    done_count = len(progress.get("done", {}))
    submissions = load_submissions()
    sub_count = len(submissions)

    if done_count == 0 and sub_count == 0:
        print(msg(args.lang, "nothing_to_reset"))
        return

    if not args.yes:
        print(msg(args.lang, "reset_confirm", done=done_count, subs=sub_count))
        print(f"  {msg(args.lang, 'reset_prompt')}", end=" ")
        try:
            answer = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            print(msg(args.lang, "reset_cancelled"))
            return
        if answer not in ("y", "yes"):
            print(msg(args.lang, "reset_cancelled"))
            return

    if PROGRESS_FILE.exists():
        os.remove(PROGRESS_FILE)
    if SUBMISSIONS_FILE.exists():
        os.remove(SUBMISSIONS_FILE)

    print(msg(args.lang, "reset_done"))


def command_export(args):
    """Export all practice data to a JSON file."""
    data = {
        "progress": load_progress(),
        "submissions": load_submissions(),
    }
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"lc_backup_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(msg(args.lang, "export_done", filename=filename))


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
    p.add_argument("--input", type=str, metavar="JSON", help="custom input as JSON, e.g. '{\"nums\": [1,2], \"target\": 3}'")
    p.set_defaults(func=command_test)
    p = sub.add_parser("done")
    add_lang(p)
    p.add_argument("id", type=int)
    p.set_defaults(func=command_done)
    p = sub.add_parser("stats")
    add_lang(p)
    p.set_defaults(func=command_stats)
    p = sub.add_parser("history")
    add_lang(p)
    p.add_argument("--yesterday", action="store_true", help="show only yesterday's submissions")
    p.set_defaults(func=command_history)
    p = sub.add_parser("footprint")
    add_lang(p)
    p.set_defaults(func=command_footprint)
    p = sub.add_parser("reset")
    add_lang(p)
    p.add_argument("--yes", action="store_true", help="skip confirmation")
    p.set_defaults(func=command_reset)
    p = sub.add_parser("export")
    add_lang(p)
    p.set_defaults(func=command_export)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
