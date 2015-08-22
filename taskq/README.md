## Task Queue

**例子**：

执行[example.py](./example.py)添加任务，用[executor.py](./executor.py)来执行任务，完整例子见，目前`max_workers`参数并不起作用...

![](http://damnever.github.io/img/post/2015-08-22-03.png)

需要执行函数必须可以`import`，如果在需要执行的函数所在的模块`ENQUEUE`，一定要避免加载模块的时候就直接`ENQUEUE`了（最好在`if __name__ == '__main__'`，或者某个不会在加载模块就执行的作用域内），不然会造成死循环... 因为`imp.load_source`会加载并**初始化**那个模块，当时文档没看清，这个里曾经困扰我好久，任务越执行越多...

---
***

任务队列的大概思路是将需要执行的任务`pickle`后存储在`Redis`里，然后让`Worker`取出来执行。

如上所述，像[rq](http://python-rq.org/)一样只能用于执行本机的`Python`代码。不过这个更简单，目前没有优先级、没有超时机制、不能依赖于其它任务、非异步执行等等等，不过有重试机制...

[tqueue.py](./tqueue.py)里有四种队列，基于`Redis`，`Queue`用来存储等待执行的任务，`SuccessQueue`存储执行成功（没有异常）的任务结果，`FailQueue`用于存储执行出现异常并需要重试的任务，`DeadQueue`用来存储用完重试次数也不能正确执行的任务异常信息。这里面`task_id`是一个关键值，将它们关联起来。

[Worker](./worker.py) 很简单，首先查看队列`Queue`里有没有等待执行的任务，如果有就执行；没有就看是否需要重试，如果需要重试查看队列`FailQueue`里是否有任务，有就执行，如果重试次数用完了，连同异常信息加入`DeadQueue`；如果不需要重试，会把出现异常的任务直接加入`DeadQueue`；若十秒内没有任务可执行，就打印运行状态。