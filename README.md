

### 依赖导出

> pip install pipreqs -i https://pypi.douban.com/simple
> pipreqs . --encoding=utf8 --force

### 依赖安装

> pip install -r requirements.txt -i https://pypi.douban.com/simple

### 启动

>  uvicorn main:app --reload --port 18080 --host 0.0.0.0