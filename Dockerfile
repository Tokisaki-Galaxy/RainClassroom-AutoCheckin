# 使用官方Python运行时作为父镜像
FROM python:3.8-slim-buster

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到容器的/app目录中
COPY . /app

# 安装项目需要的包
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV RUNNING_IN_DOCKER=true

# 运行__main__.py
CMD ["python", "./__main__.py"]