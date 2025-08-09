from dbgpt import model
from dbgpt._private.pydantic import BaseModel,Field
from dbgpt.core.awel.dag.base import DAG
from dbgpt.core.awel.operators.common_operator import MapOperator
from dbgpt.core.awel.trigger.http_trigger import HttpTrigger
from dbgpt.core.interface.llm import ModelRequest
from dbgpt.core.interface.message import ModelMessage
from dbgpt.model.operators.llm_operator import LLMOperator
from dbgpt.model.proxy import MoonshotLLMClient

class TriggerReqBody(BaseModel):
    model: str = Field(..., description="Model name")
    user_input: str = Field(..., description="User input")

class RequestHandleOperator(MapOperator[TriggerReqBody, ModelRequest]):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    async def map(self, input_value: TriggerReqBody) -> ModelRequest:
        messages = [ModelMessage.build_human_message(input_value.user_input)]
        print(f"Receive input value: {input_value}")
        return ModelRequest(model=input_value.model, messages=messages)


with DAG("dbgpt_awel_simple_dage_example") as dag:
    trigger = HttpTrigger("/examples/simple_chat",methods="POST",request_body=TriggerReqBody)
    request_handle_task = RequestHandleOperator()
    # 默认是openai的模型，
    # llm_task = LLMOperator(task_name="llm_task")
    llm_task = LLMOperator(task_name="llm_task",llm_client=MoonshotLLMClient())
    model_parse_task = MapOperator(lambda out: out.to_dict())
    trigger >> request_handle_task >> llm_task >> model_parse_task


if __name__ == "__main__":
    if dag.leaf_nodes[0].dev_mode:
        from dbgpt.core.awel import setup_dev_environment
        setup_dev_environment([dag],port=5555)
    else:
        pass



