# **命令**

```bash
$ CheeseAPI -h
usage: CheeseAPI [-h] [--app [APP]] [--host [HOST]] [--port [PORT]] [--reload [RELOAD]] [--workers [WORKERS]] [--log_path [LOG_PATH]] [--log_filename [LOG_FILENAME]]

options:
  -h, --help            show this help message and exit
  --app [APP]           服务器本服务【默认值：app:app】
  --host [HOST]         服务器地址【默认值：127.0.0.1】
  --port [PORT]         端口号【默认值：5214】
  --reload [RELOAD]     热更新。与workers冲突【默认值：False】
  --workers [WORKERS]   workers为0时会自动设置为cpu核数*2。与reload冲突【默认值：1】
  --log_path [LOG_PATH]
                        日志文件夹的相对路径【默认值：/logs/】
  --log_filename [LOG_FILENAME]
                        日志文件名。当值为True时，自动设置为%Y_%m_%d-%H_%M_%S.log；当值为False，关闭日志文件记录；自定义文件名也是允许的【默认值：True】
```
