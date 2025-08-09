import asyncio
from typing import AsyncIterator
from dbgpt.core.awel.dag.base import DAG
from dbgpt.core.awel.operators.stream_operator import StreamifyAbsOperator, TransformStreamAbsOperator


class NumberProducerOperator(StreamifyAbsOperator[int,int]):
    async def streamify(self, n: int) -> AsyncIterator[int]:
        print('xxxxxxxxxxxxxxxxx')
        for i in range(n):
            yield i


class NumberDoubleOperator(TransformStreamAbsOperator[int,int]):
    async def transform_stream(self, it: AsyncIterator) -> AsyncIterator[int]:
        async for i in it:
            yield i * 2

with DAG("number_dag") as dag:
    task = NumberProducerOperator()
    double_task = NumberDoubleOperator()
    task >> double_task

async def help_call_fn(t, n: int):
    async for i in await t.call_stream(call_data=n):
        print(i)

asyncio.run(help_call_fn(double_task, 10))