import sys

from common_tool.server import init_base, MultiM
from config import get_workers

worker_id = sys.argv[1]

init_base("config.yaml", log_f_prefix="worker")
worker = get_workers()[worker_id]
worker.set_local()
MultiM.add_p("worker", worker.start)
MultiM.start()
