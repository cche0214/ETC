# 02_前端架构 (Frontend Architecture)

## 1. 技术概览
*   **框架**：Vue.js (Vue 2/3)
*   **UI 组件库**：Element UI / Element Plus
*   **图表库**：ECharts (用于大屏可视化展示)
*   **构建工具**：Vite (根据 `vite.config.js`)
*   **交互模式**：SPA (单页应用)

## 2. 项目结构 (`etc-visualization`)
前端项目主要位于 `visualization/etc-visualization` 目录下：
*   `public/`：静态资源。
*   `src/`：源代码。
    *   `components/`：Vue 组件。
    *   `views/`：页面视图（如 Dashboard, QueryPage）。
    *   `api/`：后端接口封装。
*   `vite.config.js`：Vite 配置文件，配置了代理等信息。
*   `index.html`：入口文件。

## 3. 核心功能模块

### 3.1 可视化大屏 (Dashboard)
*   **数据来源**：
    *   **实时数据**：通过轮询 (Polling) 或 SSE (Server-Sent Events) 从后端获取 Redis 中的实时流量统计。
    *   **展示维度**：
        *   **车辆总数**：当日累计过车流量。
        *   **跨省/市流动**：基于 `BOUNDARY_LEVEL` 字段统计省际和市际交通流。
        *   **实时流量趋势**：展示最近 1 小时内的分钟级流量变化。
        *   **异常报警**：实时滚动展示套牌车报警信息 (`Traffic:Alert:Decked`)。

### 3.2 交互式查询界面 (Interactive Query)
*   **功能**：集成 LLM Agent 的聊天界面。
*   **交互流程**：
    1.  用户输入自然语言问题（如“帮我查一下昨天G3高速的流量”）。
    2.  前端通过 POST 请求发送给 FastAPI 后端 (`/api/chat/sessions/{id}/messages`)。
    3.  后端返回 SSE 流式响应 (`text/event-stream`)。
    4.  前端实时渲染 AI 的思考过程 (Thought) 和最终 SQL 结果 (Final Answer)。

### 3.3 实时报警 (Alert System)
*   **逻辑**：前端定时请求后端接口，后端查询 Redis List (`Traffic:Alert:Decked`) 返回最新的套牌嫌疑记录。
*   **展示**：在大屏右侧或底部以跑马灯或列表形式展示。

## 4. 接口交互
前端默认与本地或远程后端服务通信：
*   **Flask/FastAPI 服务端口**：`8001` (Agent 服务) 或 `8080` (原 Flask 服务)。
*   **开发环境代理**：在 `vite.config.js` 中配置了 `server.proxy` 以解决跨域问题，将 `/api` 转发至后端服务。

