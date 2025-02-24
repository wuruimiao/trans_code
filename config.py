from common_tool.log import logger
from common_tool.system import run_cmd
from common_tool.errno import Error, OK
from common_tool.config import get_conf
from dist_task.file import FileTask
from dist_task.file import FileWorker

H265 = Error(2222, "h265_fail", "h265失败")


def get_workers():
    worker_config = get_conf('workers')

    workers: dict[str, FileWorker] = {conf['host']: FileWorker(
        conf["status"], conf["task"], conf['host'], conf["con"])
        for conf in worker_config}
    for worker in workers.values():
        worker.set_handler(do)
    return workers


def do(task: FileTask) -> Error:
    output, ok = run_cmd(["./trans_code/h265_video.sh", task.task_dir], timeout=3 * 60 * 60)
    logger.info(f"h265 {task.id} {output}")
    if ok:
        return OK
    return H265
