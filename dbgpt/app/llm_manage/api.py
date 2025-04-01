from typing import List
from fastapi import APIRouter

from dbgpt._private.config import Config
from dbgpt.app.llm_manage.model_instance_db import ModelInstance, ModelInstanceDao, ModelInstanceParams
from dbgpt.app.llm_manage.request.request import ModelResponse
from dbgpt.app.openapi.api_view_model import Result
from dbgpt.component import ComponentType
from dbgpt.model.cluster import WorkerManagerFactory, WorkerStartupRequest
from dbgpt.model.cluster.manager_base import WorkerRunData

CFG = Config()
router = APIRouter()

@router.get("/v1/worker/model/params")
async def model_params():
    print(f"/worker/model/params")
    try:
        from dbgpt.model.cluster import WorkerManagerFactory

        worker_manager = CFG.SYSTEM_APP.get_component(
            ComponentType.WORKER_MANAGER_FACTORY, WorkerManagerFactory
        ).create()
        params = []
        workers = await worker_manager.supported_models()
        for worker in workers:
            for model in worker.models:
                model_dict = model.__dict__
                model_dict["host"] = worker.host
                model_dict["port"] = worker.port
                params.append(model_dict)
        return Result.succ(params)
        if not worker_instance:
            return Result.failed(code="E000X", msg=f"can not find worker manager")
    except Exception as e:
        return Result.failed(code="E000X", msg=f"model stop failed {e}")


@router.get("/v1/worker/model/list_config")
async def model_list_config():
    print(f"/worker/model/list_config")
    try:
        from dbgpt.model.cluster.controller.controller import BaseModelController

        controller = CFG.SYSTEM_APP.get_component(
            ComponentType.MODEL_CONTROLLER, BaseModelController
        )
        responses = []
        managers = await controller.get_all_instances(
            model_name="WorkerManager@service", healthy_only=True
        )
        manager_map = dict(map(lambda manager: (manager.host, manager), managers))
        models = await controller.get_all_instances()
        for model in models:
            worker_name, worker_type = model.model_name.split("@")
            if worker_type == "llm" or worker_type == "text2vec":
                response = ModelResponse(
                    model_name=worker_name,
                    model_type=worker_type,
                    host=model.host,
                    port=model.port,
                    healthy=model.healthy,
                    check_healthy=model.check_healthy,
                    last_heartbeat=model.last_heartbeat,
                    prompt_template=model.prompt_template,
                )
                response.manager_host = (
                    model.host if manager_map.get(model.host) else None
                )
                response.manager_port = (
                    manager_map[model.host].port
                    if manager_map.get(model.host)
                    else None
                )
                responses.append(response)
        return Result.succ(responses)

    except Exception as e:
        return Result.failed(code="E000X", msg=f"model list error {e}")




@router.get("/v1/worker/model/list")
async def model_list():
    print(f"/worker/model/list")
    try:

        from dbgpt.model.cluster.controller.controller import BaseModelController

        controller = CFG.SYSTEM_APP.get_component(
            ComponentType.MODEL_CONTROLLER, BaseModelController
        )
        # 模型内存实例
        models = await controller.get_all_instances()
        
        dao = ModelInstanceDao()
        model_instances = dao.get_list({})

        responses = []
        for model_instance in model_instances:
            # 判断数据库模型是否在内存实例中存在
            if model_instance.model not in [model.model_name for model in models]:
                worker_manager = CFG.SYSTEM_APP.get_component(
                 ComponentType.WORKER_MANAGER_FACTORY, WorkerManagerFactory
                ).create()
                if not worker_manager:
                    return Result.failed(code="E000X", msg=f"can not find worker manager")
                
                startup_init_instances: List[WorkerRunData] = await worker_manager.get_all_model_instances('llm',False)

                # 不存在则进行写入到内存
                worker_request = WorkerStartupRequest(
                    host=model_instance.host,
                    port=model_instance.port,
                    model=model_instance.model,
                    params=model_instance.params.dict(),
                    worker_type=model_instance.worker_type
                )
                # 判断模型是否已经初始化启动
                if model_instance.model not in [startup_init_instance.worker_params.model_name for startup_init_instance in startup_init_instances]:
                    startup_result = await worker_manager.model_startup(worker_request)
                
            response = ModelResponse(
                model_name=model_instance.model,
                model_type=model_instance.params.model_type,
                host=model_instance.host,
                port=model_instance.port,
                healthy=True,  # Assuming all models are healthy if they are in the database
                check_healthy=True,  # Assuming all models are healthy if they are in the database
                last_heartbeat=None,  # Assuming last_heartbeat is not stored in the database
                prompt_template=model_instance.params.prompt_template,
            )
            response.manager_host = model_instance.host  # Assuming manager_host is not stored in the database
            response.manager_port = model_instance.port  # Assuming manager_port is not stored in the database
            responses.append(response)
        return Result.succ(responses)

    except Exception as e:
        return Result.failed(code="E000X", msg=f"model list error {e}")


@router.post("/v1/worker/model/stop")
async def model_stop(request: WorkerStartupRequest):
    print(f"/v1/worker/model/stop:")
    try:
        from dbgpt.model.cluster.controller.controller import BaseModelController

        worker_manager = CFG.SYSTEM_APP.get_component(
            ComponentType.WORKER_MANAGER_FACTORY, WorkerManagerFactory
        ).create()
        if not worker_manager:
            return Result.failed(code="E000X", msg=f"can not find worker manager")
        request.params = {}
        return Result.succ(await worker_manager.model_shutdown(request))
    except Exception as e:
        return Result.failed(code="E000X", msg=f"model stop failed {e}")


@router.post("/v1/worker/model/start")
async def model_start(request: WorkerStartupRequest):
    print(f"/v1/worker/model/start:")
    try:
        worker_manager = CFG.SYSTEM_APP.get_component(
            ComponentType.WORKER_MANAGER_FACTORY, WorkerManagerFactory
        ).create()
        if not worker_manager:
            return Result.failed(code="E000X", msg=f"can not find worker manager")


        dao = ModelInstanceDao()
        db = dao.get_raw_session()
        # Insert or update model information in the database
        model_name = request.model
        model_instance = db.query(ModelInstance).filter_by(model=model_name).first()
        if not model_instance:
            model_instance_params = ModelInstanceParams(**request.params)
            model_instance = ModelInstance(
                host=request.host,
                port=request.port,
                model=model_name,
                worker_type=request.worker_type,
                params=model_instance_params
            )
            db.add(model_instance)
        else:
            model_instance.host = request.host
            model_instance.port = request.port
            model_instance.worker_type = request.worker_type
            model_instance.params = ModelInstanceParams(**request.params)
        db.commit()
        # 启动完成后，才能添加到内存中，因为要进行健康状态检查
        startup_result = await worker_manager.model_startup(request)
        return Result.succ(startup_result)

    except Exception as e:
        return Result.failed(code="E000X", msg=f"model start failed {e}")
