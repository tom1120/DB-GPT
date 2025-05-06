from click import prompt
from dbgpt.core.awel.dag.base import DAG
from dbgpt.core.interface.operators.llm_operator import RequestBuilderOperator
from dbgpt.core.interface.operators.prompt_operator import PromptBuilderOperator
from dbgpt.core.interface.output_parser import BaseOutputParser
from dbgpt.model.operators.llm_operator import LLMOperator
from dbgpt.model.proxy.llms.moonshot import MoonshotLLMClient
# from dbgpt.model.proxy.llms.chatgpt import OpenAILLMClient



with DAG('simple_sdk_llm_example_dag') as dag:
    prompt_task = PromptBuilderOperator(
        "Write a SQL of {dialect} to query all dat of  {table_name}"
    )

    model_pre_handler_task = RequestBuilderOperator(model="moonshot-v1-8k")
    llm_task = LLMOperator(MoonshotLLMClient())
    out_parse_task = BaseOutputParser()

    print(out_parse_task)

    prompt_task >> model_pre_handler_task >> llm_task >> out_parse_task