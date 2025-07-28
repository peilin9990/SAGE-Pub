# DataStream 编程指南

SAGE 中的 DataStream 是对数据流进行转换处理的应用程序。如图所示：数据流的起始是从各种源（例如消息队列、套接字流、文件）创建的，经过各种算子处理，结果通过 sink 返回，例如可以将数据写入文件或标准输出（例如命令行终端）。

![DataStream Processing](../../assets/img/streaming.png)

为了创建自己的 SAGE DataStream 程序，我们建议您从 Hello World 程序剖析开始，然后逐渐添加自己的 stream transformation。

## Hello World 程序剖析

