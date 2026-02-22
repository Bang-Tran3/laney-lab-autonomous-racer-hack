from __future__ import annotations

import argparse
import time
from pathlib import Path

from trainer.api_client import TrainerApiClient
from trainer.train_job_runner import run_job


def main() -> None:
    parser = argparse.ArgumentParser(description="Poll queued training jobs and run the trainer scaffold.")
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--output-root", default="services/trainer/data")
    parser.add_argument("--poll-seconds", type=int, default=15)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--set-active", action="store_true")
    args = parser.parse_args()

    api = TrainerApiClient(args.api_url)
    output_root = Path(args.output_root)

    while True:
        queued = api.list_training_jobs(status="queued", limit=10)
        for job in queued:
            run_job(args.api_url, job["job_id"], output_root=output_root, set_active=args.set_active)

        if args.once:
            break
        time.sleep(max(1, args.poll_seconds))


if __name__ == "__main__":
    main()
