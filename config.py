from common_tool.log import logger
from common_tool.system import run_cmd
from common_tool.errno import Error, OK
from common_tool.config import get_conf
from dist_task.file import FileTask
from dist_task.file import FileWorker

H265 = Error(2222, "h265_fail", "h265失败")


def get_workers():
    worker_config = get_conf('workers')
    workers: dict[str, FileWorker] = {}

    for conf in worker_config:
        worker_id = conf['host']
        worker = FileWorker(conf["status"], conf["task"], worker_id, conf["con"])
        on_yun = conf.get('on_yun', True)
        logger.info(f'{worker_id} on_yun={on_yun}')
        worker.set_handler(handler(on_yun))
        workers[worker_id] = worker
    return workers


def handler(on_yun):
    def do(task: FileTask) -> Error:
        task_dir, _ = task.task_dir()
        logger.info(f'start h265 {task.id} {task_dir}')
        output, ok = run_cmd(
            ["./h265_video.sh", task_dir, {True: 'true', False: 'false'}[on_yun]],
            timeout=3 * 60 * 60)
        logger.info(f"end h265 {task.id} {task_dir} {output}")
        if ok:
            return OK
        return H265
    return do
