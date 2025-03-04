 1. 这个项目是基于CUDA11.8构建的，如果CUDA不是11.8版本，需要重新安装驱动，比较麻烦。
目前了解到10.0的CUDA版本，但是启动就内存异常
pycharm run或者debug，执行到_initialize_model_cache(system_app, param.port)，触发windows 内存访问异常，终止执行。


# from rocksdict import Options, Rdict
from speedict import Options, Rdict


pip uninstall dbgpt
pip install -e .
使用 -e 选项进行开发模式安装，这样可以确保代码不会被复制到 site-packages，而是通过符号链接指向源代码目录。

pip install speedict