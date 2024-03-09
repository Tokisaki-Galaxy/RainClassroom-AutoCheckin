# 使用官方Python运行时作为父镜像
FROM python:3.11.5-slim

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到容器的/app目录中
COPY . /app

# 更新pip和setuptools
RUN if [ "$USE_CHINA_MIRROR" = "true" ] ; then \
    pip install -i https://mirrors.aliyun.com/pypi/simple/ --upgrade pip setuptools wheel ; \
else \
    pip install --upgrade pip setuptools wheel ; \
fi

# 安装项目需要的包
RUN if [ "$USE_CHINA_MIRROR" = "true" ] ; then \
    pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r requirements.txt ; \
else \
    pip install --no-cache-dir -r requirements.txt ; \
fi

# 设置环境变量
ENV RUNNING_IN_DOCKER=true

# 运行__main__.py
CMD ["python", "./__main__.py"]