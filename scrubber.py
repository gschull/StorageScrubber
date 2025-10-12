#!/usr/bin/env python3
"""
Storage Scrubber - CLI entrypoint
"""
import argparse
import sys
from scrubber.core import StorageScrubber


def main(argv=None):
    parser = argparse.ArgumentParser(prog="scrubber", description="Scan and clean storage to free space")
    parser.add_argument("path", nargs="?", default=".", help="Path to scan")
    parser.add_argument("--dry-run", action="store_true", help="Don't delete anything; just report")
    parser.add_argument("--auto-clean", action="store_true", help="Automatically delete files matching auto-rules (temp, cache, updates)")
    parser.add_argument("--find-duplicates", action="store_true", help="Find duplicate files by content (may be slow)")
    parser.add_argument("--top", type=int, default=20, help="Show top N largest files in the report")
    parser.add_argument("--exclude", action='append', default=[], help="Path substring to exclude (repeatable)")
    parser.add_argument("--interactive-delete", action='store_true', help="Ask per-file before deleting during auto-clean")
    parser.add_argument("--permanent", action='store_true', help="Permanently delete files instead of moving to Recycle Bin (dangerous)")
    parser.add_argument("--min-size", type=int, default=0, help="Minimum file size in bytes to consider")
    parser.add_argument("--min-age", type=int, default=0, help="Minimum file age in days to consider")
    parser.add_argument("--report-json", type=str, help="Write JSON report to file")
    parser.add_argument("--yes", "-y", action="store_true", help="Assume yes for delete confirmations")

    args = parser.parse_args(argv)

    ss = StorageScrubber(root=args.path)
    report = ss.scan(min_size=args.min_size, min_age_days=args.min_age, exclude_patterns=args.exclude)

    print(ss.summary(report))

    if args.report_json:
        ss.write_json_report(report, args.report_json)
        print(f"Wrote JSON report to {args.report_json}")

    if args.auto_clean:
        to_delete = ss.select_auto_clean(report)
        print(f"Auto-clean candidate count: {len(to_delete)}")
        if args.dry_run:
            print("Dry run: not deleting files")
        else:
            ss.delete_files(to_delete, confirm=args.yes, interactive=args.interactive_delete, permanent=args.permanent)

    if args.find_duplicates:
        print("Searching for duplicate files (this may take a while)...")
        groups = ss.find_duplicates(report)
        if not groups:
            print("No duplicates found")
        else:
            print(f"Found {len(groups)} duplicate groups")
            for g in groups:
                print("Group:")
                for f in g:
                    print(f"  {f.path} ({f.size} bytes)")

    topn = ss.top_files(report, n=args.top)
    if topn:
        print(f"\nTop {len(topn)} largest files:")
        for f in topn:
            print(f"  {f.path} — {ss._format_size(f.size)}")


if __name__ == "__main__":
    main()
