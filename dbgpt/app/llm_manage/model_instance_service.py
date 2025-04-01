import asyncio
from dbgpt.app.component_configs import CFG
from dbgpt.app.llm_manage.model_instance_db import ModelInstanceDao
from dbgpt.app.openapi.api_view_model import Result
from dbgpt.component import ComponentType
from dbgpt.model.cluster.base import WorkerStartupRequest
from dbgpt.model.cluster.manager_base import WorkerManagerFactory


def model_startup_from_db():
    try:
        from dbgpt.model.cluster.controller.controller import BaseModelController

        controller = CFG.SYSTEM_APP.get_component(
            ComponentType.MODEL_CONTROLLER, BaseModelController
        )
        # 模型内存实例
        models = asyncio.run(controller.get_all_instances())
        dao = ModelInstanceDao()
        model_instances = dao.get_list({})
        for model_instance in model_instances:
            # 判断数据库模型是否在内存实例中存在
            if model_instance.model not in [model.model_name for model in models]:
                worker_manager = CFG.SYSTEM_APP.get_component(
                 ComponentType.WORKER_MANAGER_FACTORY, WorkerManagerFactory
                ).create()
                if not worker_manager:
                    return Result.failed(code="E000X", msg=f"can not find worker manager")
                # 不存在则进行写入到内存
                worker_request = WorkerStartupRequest(
                    host=model_instance.host,
                    port=model_instance.port,
                    model=model_instance.model,
                    params=model_instance.params.dict(),
                    worker_type=model_instance.worker_type
                )
                startup_result = asyncio.run(worker_manager.model_startup(worker_request))
    except Exception as e:
        return Result.failed(code="E000X", msg=f"model list error {e}")