import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from personnel.models import Personnel

logger = logging.getLogger(__name__)

def check_expired_personnel():
    """检查并更新已到期的人员状态"""
    try:
        updated_count, updated_names = Personnel.check_and_update_expired_personnel()

        if updated_count > 0:
            logger.info(f"定时任务执行成功：将 {updated_count} 名人员设置为已卸任状态")
            logger.info(f"更新的人员：{', '.join(updated_names)}")
        else:
            logger.info("定时任务执行成功：没有需要更新的人员")

    except Exception as e:
        logger.error(f"定时任务执行失败：{str(e)}")

@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """删除旧的任务执行记录（默认保留7天）"""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

def start_scheduler():
    """启动定时任务调度器"""
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # 添加人员到期检测任务 - 每天早上8点执行
    scheduler.add_job(
        check_expired_personnel,
        trigger="cron",
        hour=8,
        minute=0,
        id="check_expired_personnel",
        max_instances=1,
        replace_existing=True,
    )
    logger.info("已添加人员到期检测定时任务：每天早上8:00执行")

    # 添加清理旧任务记录的任务 - 每周执行一次
    scheduler.add_job(
        delete_old_job_executions,
        trigger="cron",
        day_of_week="mon",
        hour=1,
        minute=0,
        id="delete_old_job_executions",
        max_instances=1,
        replace_existing=True,
    )
    logger.info("已添加清理旧任务记录任务：每周一凌晨1:00执行")

    try:
        logger.info("正在启动定时任务调度器...")
        scheduler.start()
        logger.info("定时任务调度器启动成功")
    except KeyboardInterrupt:
        logger.info("正在停止定时任务调度器...")
        scheduler.shutdown()
        logger.info("定时任务调度器已停止")
