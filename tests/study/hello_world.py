import asyncio
from dbgpt.core.awel.dag.base import DAG
from dbgpt.core.awel.operators.common_operator import InputOperator, MapOperator
from dbgpt.core.awel.task.task_impl import SimpleCallDataInputSource


with DAG("awel_hello_world") as dag:
    input_task = InputOperator(input_source=SimpleCallDataInputSource())
    task = MapOperator(map_function=lambda x: print(f"Hello, {x}!"))
    input_task >> task

# dag.visualize_dag()
asyncio.run(task.call(call_data="world"))