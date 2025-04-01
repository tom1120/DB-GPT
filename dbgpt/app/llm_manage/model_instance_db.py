from datetime import datetime
from turtle import st
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field
from regex import F
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, TypeDecorator

import sqlalchemy
from sqlalchemy.sql import func

from dbgpt.storage.metadata import Model,BaseDao

class ModelInstanceParams(BaseModel):
    model_name: str=Field(description="模型名称")
    model_path: str=Field(description="模型路径")
    proxy_server_url: str=Field(description="代理服务器地址")
    proxy_api_key: str=Field(description="代理服务器api key")
    proxy_api_base: Optional[str]=Field(default=None,description="代理服务器api base")
    proxy_api_app_id: Optional[str]=Field(default=None,description="代理服务器api app id")
    proxy_api_secret: Optional[str]=Field(default=None,description="代理服务器api secret")
    proxy_api_type: Optional[str]=Field(default=None,description="代理服务器api type")
    proxy_api_version:Optional[str]=Field(default=None,description="代理服务器api version")
    http_proxy:Optional[str]=Field(default=None,description="代理服务器http代理")
    proxyllm_backend:Optional[str]=Field(default=None,description="代理服务器proxyllm backend")
    model_type: Optional[str]=Field(default=None,description="模型类型")
    device: Optional[str]=Field(default=None,description="设备类型")
    prompt_template: Optional[str]=Field(default=None,description="模型提示模板")
    max_context_size: int=Field(default=4096,description="模型最大上下文长度")
    llm_client_class: Optional[str]=Field(default=None,description="模型客户端类")


class _PydanticType(TypeDecorator):
    impl=sqlalchemy.types.JSON

    def __init__(self, pydantic_type:BaseModel):
        super().__init__()
        self._pydantic_type = pydantic_type
    
    def process_bind_param(self, value, dialect):
        return value.dict()
    
    def process_result_value(self, value, dialect):
        return self._pydantic_type.parse_obj(value)


class ModelInstance(Model):
    __tablename__ = 'model_instance'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    host = Column(String(100),nullable=False)
    port = Column(Integer,nullable=False)
    model  = Column(String(100),nullable=False)
    worker_type = Column(String(100),nullable=False)
    params = Column(_PydanticType(ModelInstanceParams),nullable=False)
    gmt_created = Column(DateTime, default=func.now())
    gmt_modified = Column(DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "host": self.host,
            "port": self.port,
            "model": self.model,
            "worker_type": self.worker_type,
            "params": self.params.dict(),
            "gmt_created": self.gmt_created,
            "gmt_modified": self.gmt_modified,
        }


class ModelInstancePydantic(BaseModel):
    id: int = Field(description="唯一标识符")
    host: str = Field(description="主机地址")
    port: int = Field(description="端口号")
    model: str = Field(description="模型名称")
    worker_type: str = Field(description="工作类型")
    params: ModelInstanceParams = Field(description="模型参数")
    gmt_created: datetime = Field(description="创建时间")
    gmt_modified: datetime = Field(description="修改时间")


class ModelInstanceDao(BaseDao[ModelInstance,BaseModel,BaseModel]):
    def create_model_instance(self, model_instance:ModelInstance):
        session = self.get_raw_session()
        session.add(model_instance)
        session.commit()
        model_instance_id = model_instance.id
        session.close()
        return model_instance_id
    
    def from_request(self, request: Union[BaseModel, Dict[str, Any]])->ModelInstance:
        request_dict = request.dict() if isinstance(request, BaseModel) else request
        model_instance = ModelInstance(**request_dict)
        return model_instance
    
    def to_response(self,model_instance: ModelInstance)->BaseModel:
        return ModelInstancePydantic(
            id=model_instance.id,
            host=model_instance.host,
            port=model_instance.port,
            model=model_instance.model,
            worker_type=model_instance.worker_type,
            params=model_instance.params,
            gmt_created=model_instance.gmt_created,
            gmt_modified=model_instance.gmt_modified
        )

if __name__ == "__main__":
    # 调用dao执行插入测试
    model_instance_params = ModelInstanceParams(
        model_name='zhipu_proxyllm',
        model_path='zhipu_proxyllm',
        proxy_server_url='https://open.bigmodel.cn/api/paas/v4/chat/completions',
        proxy_api_key='79f30b4f06549b9f95d4309e8373f170.bA7un4PnUtZ2UPBl',
        proxy_api_base='',
        proxy_api_app_id='',
        proxy_api_secret='',
        proxy_api_type='',
        proxy_api_version='',
        http_proxy='',
        proxyllm_backend='',
        model_type='llm',
        device='cpu',
        prompt_template='',
        maximum_context_size=4096,
        llm_client_class=None
    )
    model_instance = ModelInstance(
        host='192.168.96.66',
        port=5670,
        model='zhipu_proxyllm',
        worker_type='llm',
        params=model_instance_params
    )
    dao = ModelInstanceDao()
    dao.create_model_instance(model_instance)
    print(dao.get_all())