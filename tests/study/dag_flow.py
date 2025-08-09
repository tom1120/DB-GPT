import asyncio
from dbgpt._private.pydantic import BaseModel,Field
from dbgpt.core.awel.dag.base import DAG
from dbgpt.core.awel.operators.common_operator import MapOperator
from dbgpt.core.awel.trigger.http_trigger import HttpTrigger


class TriggerReqBody(BaseModel):
    name: str = Field(..., description="user name")
    age: int = Field(18, description="user age")


class RequestHandleOperator(MapOperator[TriggerReqBody, str]):
    def __init__(self,**kwargs):
        super().__init__(**kwargs) 
    async def map(self,input_value: TriggerReqBody) -> str:
        print(f"Receive input value: {input_value}")
        return f"Hello {input_value.name}, you are {input_value.age} years old."

with DAG("simple_dag_example") as dag:
    trigger = HttpTrigger("/examples/hello",request_body=TriggerReqBody)
    map_code = RequestHandleOperator()
    trigger >> map_code


# asyncio.run(map_code.call(call_data=TriggerReqBody(name="dbgpt",age=18)))

# curl -X GET http://127.0.0.1:5555/api/v1/awel/trigger/examples/hello?name=zhangsan
if __name__ == "__main__":
    if dag.leaf_nodes[0].dev_mode:
        from dbgpt.core.awel import setup_dev_environment

        setup_dev_environment([dag],port=5555)
    else:
        pass