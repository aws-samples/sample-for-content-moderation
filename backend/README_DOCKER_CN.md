# 构建基于 Python 和 FFmpeg 的基础镜像

## 创建 Dockerfile 文件

```dockerfile
FROM python:3.11-alpine

LABEL authors="tedli"

# 安装 ffmpeg
RUN apk add --no-cache ffmpeg

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 到容器中
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置默认命令
CMD ["/bin/sh"]
```

## 构建多架构镜像

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t ffmpeg6_python311_m:v01 .
```

## 给镜像打标签

```bash
docker tag ffmpeg6_python311_m:v01 yyyyyy/ffmpeg6_python311_m:v01
```

## 推送到远程仓库

```bash
docker push yyyyyy/ffmpeg6_python311_m:v01
```
