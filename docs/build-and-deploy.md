# QuizForge 构建与部署指南

## 目录

- [环境要求](#环境要求)
- [本地开发](#本地开发)
- [构建桌面应用](#构建桌面应用)
  - [Windows](#windows)
  - [macOS](#macos)
- [构建 Web 版本](#构建-web-版本)
- [Docker 部署](#docker-部署)
  - [Docker 直接运行](#docker-直接运行)
  - [Docker Compose](#docker-compose)
  - [自定义题库目录](#自定义题库目录)
- [CI/CD 自动发布](#cicd-自动发布)
  - [触发构建](#触发构建)
  - [产物说明](#产物说明)
  - [拉取 Docker 镜像](#拉取-docker-镜像)
- [版本号管理](#版本号管理)

---

## 环境要求

| 工具 | 版本 | 用途 |
|------|------|------|
| Node.js | >= 20 | 前端构建 |
| Rust | stable | 桌面端 Tauri 后端 |
| Docker | >= 24 | Web 版容器部署（可选） |

---

## 本地开发

```bash
# 安装依赖
npm install

# 启动 Web 开发服务器（纯前端，不含 Tauri）
npm run dev

# 启动 Tauri 开发模式（桌面端 + 前端热重载）
npm run tauri dev
```

开发服务器默认监听 `http://localhost:1420`。

---

## 构建桌面应用

### Windows

**方式一：双击脚本**

直接双击 `scripts/build-win.bat`。

**方式二：命令行**

```powershell
# PowerShell
powershell -ExecutionPolicy Bypass -File scripts/build-win.ps1
```

**方式三：手动执行**

```powershell
npm install
npm run tauri build
```

构建产物位于：

```
src-tauri/target/release/bundle/
├── msi/        # .msi 安装包
└── nsis/       # .exe 安装包
```

### macOS

```bash
bash scripts/build-mac.sh
```

或手动执行：

```bash
npm install
npm run tauri build
```

构建产物位于：

```
src-tauri/target/release/bundle/
├── dmg/        # .dmg 磁盘映像
└── macos/      # .app 应用包
```

---

## 构建 Web 版本

```bash
bash scripts/build-web.sh
```

或手动执行：

```bash
npm install
npm run build
```

产物输出到 `dist/` 目录，可直接部署到任意静态文件服务器或用于 Docker 构建。

本地预览：

```bash
npx vite preview
```

---

## Docker 部署

Web 版本使用 Caddy 作为静态服务器，支持 SPA 路由、gzip 压缩和静态资源长缓存。

### Docker 直接运行

```bash
# 构建镜像
docker build -t quizforge .

# 运行容器
docker run -d \
  --name quizforge \
  -p 8080:80 \
  -v $(pwd)/quiz-banks:/srv/quiz-banks \
  quizforge
```

访问 `http://localhost:8080`。

### Docker Compose

```bash
# 构建并启动
docker compose up -d

# 查看日志
docker compose logs -f

# 停止
docker compose down

# 重新构建（代码更新后）
docker compose up -d --build
```

默认端口映射为 `8080:80`，可在 `docker-compose.yml` 中修改。

### 自定义题库目录

题库文件（`.db`）通过卷挂载到容器内：

```bash
# 默认挂载路径
./quiz-banks:/srv/quiz-banks

# 自定义路径
docker run -d -p 8080:80 -v /path/to/your/banks:/srv/quiz-banks quizforge
```

---

## CI/CD 自动发布

项目使用 GitHub Actions，推送版本 tag 时自动构建并发布。

### 触发构建

```bash
# 1. 更新版本号（package.json + tauri.conf.json）
# 2. 提交变更
git add -A
git commit -m "release: v0.2.0"

# 3. 打 tag 并推送
git tag v0.2.0
git push origin main --tags
```

推送 `v*` 格式的 tag 后，GitHub Actions 自动执行：

| Job | 运行环境 | 产物 |
|-----|----------|------|
| `build-tauri` (Windows) | `windows-latest` | `.msi` / `.exe` 安装包 |
| `build-tauri` (macOS) | `macos-latest` | `.dmg` 磁盘映像 |
| `build-docker` | `ubuntu-latest` | Docker 镜像推送至 GHCR |

### 产物说明

桌面安装包自动上传到 GitHub Releases 页面：

```
https://github.com/RyanZhou416/QuizForge/releases/tag/v0.2.0
```

### 拉取 Docker 镜像

CI 自动推送镜像到 GitHub Container Registry（GHCR）：

```bash
# 拉取最新版
docker pull ghcr.io/ryanzhou416/quizforge:latest

# 拉取指定版本
docker pull ghcr.io/ryanzhou416/quizforge:v0.2.0
docker pull ghcr.io/ryanzhou416/quizforge:0.2.0

# 使用 GHCR 镜像运行
docker run -d -p 8080:80 ghcr.io/ryanzhou416/quizforge:latest
```

---

## 版本号管理

发布新版本时需同步更新两处版本号：

1. `package.json` — `"version"` 字段
2. `src-tauri/tauri.conf.json` — `"version"` 字段

然后打对应的 git tag（如 `v0.2.0`）触发 CI 构建。
