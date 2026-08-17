# OOCL 2026 AI Agent Training

Hello World 级环境验证工程：学员 clone 后用 **浏览器里的 Jupyter** 跑通 notebook，确认 Python / LangGraph 1.x / LLM API 均可正常工作。

> **不需要 IntelliJ / PyCharm / VS Code。** 本仓以 Jupyter Lab 网页服务为唯一推荐验证入口。

## 环境要求

- Python **3.12+**
- 推荐安装 [uv](https://docs.astral.sh/uv/)
- 任意现代浏览器（Chrome / Edge / Firefox / Safari）
- 可用的 OpenAI-compatible 模型入口（OpenRouter / OpenAI / DeepSeek / 本地 Ollama 等）

## 三步跑通（浏览器 Jupyter）

在终端执行（始终在**仓库根目录**）：

```bash
cd oocl-2026-ai-agent-training
uv sync --extra dev
cp .env.example .env   # 填写 LLM_BASE_URL、LLM_MODEL；云服务再填 LLM_API_KEY
```

注册本项目专用 Kernel（只需做一次，浏览器里好选对 Python 3.12+）：

```bash
uv run python -m ipykernel install --user \
  --name=oocl-2026-ai-agent \
  --display-name="OOCL 2026 AI Agent"
```

启动 Jupyter Lab **网站服务**，用浏览器打开终端给出的本地地址：

```bash
uv run jupyter lab
```

典型输出类似：

```text
http://localhost:8888/lab?token=...
```

在浏览器中：

1. 左侧打开 `notebooks/01-environment-hello.ipynb`
2. 右上角 Kernel 选择 **OOCL 2026 AI Agent**（不要选系统自带的旧 Python）
3. 菜单 **Run → Run All Cells**，或选中代码格后点击工具栏 ▶ 执行
4. 看到 `L0 env ok` 后，再打开 `notebooks/02-min-graph.ipynb`，同样跑通，看到 `L0 graph ok`

![在 Jupyter Lab 中选中代码格后点击执行](docs/jupyter-run-cell.png)

完成后可在终端 `Ctrl+C` 结束 Jupyter 服务。

### API Key 配置

用任意文本编辑器编辑仓库根目录的 `.env`（可用记事本 / TextEdit，不必装 IDE）：

```text
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openai/gpt-4o-mini
LLM_API_KEY=sk-...
```

说明：

- `LLM_BASE_URL` 一般以 `/v1` 结尾
- 本地不鉴权服务可将 `LLM_API_KEY` 留空
- 改完 `.env` 后，在 notebook 里 **Restart Kernel → Run All** 再验一次

### 纯 pip 备用（无 uv 时）

```bash
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m ipykernel install --user --name=oocl-2026-ai-agent --display-name="OOCL 2026 AI Agent"
jupyter lab                        # 浏览器打开给出的 http://localhost:8888/...
```

## Notebook 通关信号

| Notebook | 验证内容 | 浏览器里预期输出 |
|----------|----------|------------------|
| `notebooks/01-environment-hello.ipynb` | Python、依赖版本、LLM Key 连通 | 模型回复 + `L0 env ok` |
| `notebooks/02-min-graph.ipynb` | 最小 Graph（单节点 + 条件边）完整 invoke | 图结构 + 结果 + `L0 graph ok` |
| `notebooks/04-memory.ipynb` | Thread Memory：同 thread 续聊 / 异 thread 失忆 | `04 short-term memory ok` / `04 long-term memory ok` |
| `notebooks/04-memory-postgres-demo.ipynb` | PostgresSaver 跨进程持久化 | `04 memory postgres persistence ok` |
| `notebooks/05-tools.ipynb` | `calculate_teu` 挂进 agent ⇄ tools | `ToolMessage` + 合计 8 TEU + `L0 tools ok` |

### 可选：04-memory Postgres 耐久（本地 Docker）

`04-memory.ipynb` 使用 In-memory 后端，进程退出即清空。若要验证 `PostgresSaver` 落库（对照官方 `list` 示例）：

```bash
docker compose -f docker/memory-postgres/docker-compose.yml up -d
uv sync --extra memory-postgres
jupyter lab notebooks/04-memory-postgres-demo.ipynb
```

默认连接：`postgres://postgres:postgres@localhost:54329/postgres?sslmode=disable`  
（账号同官方示例；端口 54329 映射容器内 5432，避免与本机 Postgres 冲突。）  
在 notebook 中执行 **Run → Run All Cells**，看到 `04 memory postgres persistence ok` 即通过。清库：

```bash
docker compose -f docker/memory-postgres/docker-compose.yml down -v
```

可选：命令行快速冒烟（不替代 notebook 验证）：

```bash
uv run python -c "from hello_agent.graph import run_hello; print(run_hello())"
```

## 可选：LangGraph Studio

用于课堂可视化演示（不阻塞主验证路径）：

```bash
uv sync --extra dev
uv run langgraph dev
```

终端会给出 Studio URL（通常类似 `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024`）。Safari 若连不上本地服务，可改用：

```bash
uv run langgraph dev --tunnel
```

## 工程结构

```text
├── pyproject.toml / uv.lock / requirements.txt
├── .env.example
├── langgraph.json
├── docs/jupyter-run-cell.png   # README 操作示意
├── src/hello_agent/
│   ├── config.py      # 读取 LLM_* 并构造 ChatOpenAI
│   └── graph.py       # 最小 Graph
└── notebooks/
    ├── 01-environment-hello.ipynb
    └── 02-min-graph.ipynb
```

## 常见问题

1. **浏览器打不开 / 找不到地址**  
   看启动 `jupyter lab` 的终端输出，复制带 `token=` 的完整 `http://localhost:8888/...` 链接。

2. **提示需要 Python 3.12+，但本机显示 3.11**  
   Kernel 选错了。右上角换成 **OOCL 2026 AI Agent**，或重新执行上面的 `ipykernel install` 后再选。

3. **`langgraph` 版本是 0.x**  
   本工程基于 1.x API。请确认 `uv sync` / `pip install -r requirements.txt` 成功，并重新选择本项目 Kernel。

4. **缺少 `LLM_BASE_URL` / `LLM_MODEL`**  
   复制 `.env.example` → `.env` 后填写；必须在**仓库根目录**启动 `jupyter lab`。

5. **401 / 鉴权失败**  
   云服务检查 `LLM_API_KEY`；确认 `LLM_BASE_URL` 是否带 `/v1`。

6. **import `hello_agent` 失败**  
   先执行 `uv sync --extra dev`（可编辑安装本包），并确认 Kernel 是本项目环境，不是系统 Python。
