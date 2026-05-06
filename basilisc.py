import sys

from tools.sku_tools.reset_mrp_fields import reset_mrp
from tools.sku_tools.fix_volumetrics import fix_door_volumetrics


JOBS = {
    "reset-mrp": reset_mrp,
    "fix-door-volumetrics": fix_door_volumetrics
}


def main():
    args = sys.argv[1:]

    if not args:
        print("Usage: basilisc2 [job] [args...]")
        return

    job_name = args[0]
    job_args = args[1:]

    job = JOBS.get(job_name)

    if job is None:
        print(f"Unknown job: {job_name}")
        return

    job(*job_args)


if __name__ == "__main__":
    main()