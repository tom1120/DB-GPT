 1. 这个项目是基于CUDA11.8构建的，如果CUDA不是11.8版本，需要重新安装驱动，比较麻烦。
目前了解到10.0的CUDA版本，但是启动就内存异常
pycharm run或者debug，执行到_initialize_model_cache(system_app, param.port)，触发windows 内存访问异常，终止执行。

