# TODO — Astro Insight

结合当前实际运行状态整理。每条都标了「为什么」和「怎么验证」，方便下次接手。

---

## 已完成（本次已验证）

### 修复 `src/llms/llm.py` 循环导入 → 解除 degraded 模式

**症状**：后端启动时 `AstroWorkflow暂未就绪，API以degraded模式启动: cannot import name 'get_llm_by_type' from partially initialized module 'src.llms.llm'`

**根因**：四条 import 绕成一个环，且环是在**模块顶层**闭合的：

```
src/llms/__init__.py:7   from .llm import ...
      ↓
src/llms/llm.py:1        from src.agents.provider_runtime import AgentRuntime
      ↓
src/agents/__init__.py   from .agents import create_agent
      ↓
src/agents/agents.py:7   from src.llms.llm import get_llm_by_type   ← 回到起点
```

执行到 `agents.py:7` 时，`src.llms.llm` 只跑完了第 1 行，`get_llm_by_type` 尚未定义，于是 ImportError。

**修法**（`src/llms/llm.py`）：把 `AgentRuntime` 的 import 从模块顶层挪进 `get_llm_by_type()` 函数体内。该函数本来就只在调用时才需要它，所以行为不变，但 `llm.py` 顶层不再有任何 import，就永远不可能再参与循环。

**顺带修掉的第二个 bug**：`src/llms/__init__.py:7` 还在从 `.llm` 里 re-export `get_configured_llm_models`，但 `llm.py` 从来没定义过它——它只存在于废弃的 `llm_legacy_backup.py`。循环一解开，这个 ImportError 立刻就会顶上。已在 `llm.py` 补了一个惰性转发函数，保住 `src.llms` 的对外接口不变。

**验证证据**：
- 两种 import 顺序都成功：`import src.llms` 与 `from src.agents import create_agent`
- `AstroWorkflow()` 能成功构造
- 临时起服务实测 `GET /health` → `{"status":"ok","workflow_ready":true,"workflow_error":null}`

### 修复设置面板「看不到保存按钮」

**症状**：用户反馈配置 API 的界面上没有保存按钮。

**根因**：按钮**一直在 DOM 里**（`<button type="button">Save</button>`），但**看不见**。`LLMSettingsPanel` 的 input/select/button 全都没有任何 Tailwind class，而 Tailwind 的 preflight 会把 button 重置为：

```css
button, [type='button'] { background-color: transparent; background-image: none; }
```

加上 `font: inherit; padding: 0` → 三个按钮渲染成**一行白色纯文本**（`Validate Save Test API`），和标签文字无法区分。同理输入框也是裸的浏览器控件。

**已做的修改**（[LLMSettingsPanel.tsx](frontend/src/components/settings/LLMSettingsPanel.tsx)）：**逻辑一行未动**，只做展示层修改——
- 改用项目自带的 [Button](frontend/src/components/ui/button.tsx) 组件（走设计系统 CSS 变量）：`Save` 为主按钮（`bg-primary`，深色主题下是近白底黑字、高对比），`Validate` / `Test API` 为 outline 次按钮
- 给 input/select 统一加边框、深色底、focus ring
- 补上 5 个 `<label>`（原先只有 placeholder，没有标签）
- key 已保存时显示「已保存」徽标
- 状态信息从裸文本改为带边框的提示框

**验证证据**：`GET /settings` 实测渲染出 3 个 `data-slot="button"` 按钮，Save 的类名确认含 `bg-primary text-primary-foreground`；已核对 `globals.css` 中 `.dark` 下 `--primary`/`--primary-foreground` 均已定义（未定义的话 `bg-primary` 会解析失败、按钮又变透明）。`tsc --noEmit` 在改动文件上零错误。

---

## P0 — 让「网页填 key 就能调模型」真正跑通

后端配置接口已经齐备，实测通过：

| 端点 | 实测结果 |
|---|---|
| `GET /api/settings/llm` | `{"has_api_key":false,"api_key":""}`（key 不回传，正确） |
| `POST /api/settings/llm/validate` | `{"valid":true,...,"runtime_dependency_installed":true}` |
| `POST /api/settings/llm` | 保存配置 |
| `POST /api/settings/llm/test` | 发一次真实请求 |
| `POST /query/stream` | SSE 流式对话 |

- [ ] **1. 重启后端**。当前 8000 端口上的进程（PID 32024）加载的还是**修复前的旧代码**，仍是 degraded。必须重启才会生效。
      ```bash
      cd backend && ./.venv/Scripts/python.exe -m uvicorn api_service.main:app --host 0.0.0.0 --port 8000
      curl http://127.0.0.1:8000/health   # 期望 "status":"ok"
      ```
- [x] **2. ✅ 已修：把 LLM 设置面板挂到路由上**（2026-10-12 完成并验证）

      设置面板的代码是**写好且功能完整**的，但**没有任何页面渲染它**——是一条断掉的引用链：

      ```
      components/settings/LLMSettingsPanel.tsx        ← 面板本体，"use client"，逻辑完整
        ↑ 被 components/panels/AstroControlCenter.tsx 引用
        ↑ 被 components/integration/AstroIntegrationPanel.tsx 引用
        ↑ ❌ 到此为止：全项目没有任何 app/ 下的 page 引用 AstroIntegrationPanel
      ```

      所以浏览器里翻遍所有页面都找不到填 API 的地方，不是你没找到，是**真的没接线**。

      面板本身没问题：`LLMSettingsPanel` 通过 `@/api/settings` 正确调用了 `fetchLLMConfig` / `validateLLMConfig` / `updateLLMConfig` / `testSavedLLMConnection`，对应后端那四个接口，字段（provider / api_format / model / base_url / api_key）也和后端完全对得上。

      **已做的修改**：
      - 新建 [src/app/settings/page.tsx](frontend/src/app/settings/page.tsx)，渲染 `<AstroIntegrationPanel />`
      - [layout.tsx:78](frontend/src/app/layout.tsx#L78) 那个 `{/* 预留右侧 */}` 空占位处，换成指向 `/settings` 的「设置」链接

      **验证证据**：dev server 实测 `GET /settings` → **200**，SSR HTML 中确认包含 `LLM Configuration`、`Provider (openai...)`、`API Key`、`Validate` 等标记；`/` 和 `/home` 顶栏均能取到 `href="/settings"`。`tsc --noEmit` 在改动文件上**零错误**。

- [ ] **2b. 前端填配置并端到端验证**：挂上路由后，填 provider / api_format / model / base_url / api_key → 点 **Validate**（不发请求、不花钱）→ **Save** → **Test API**（发一次最小真实请求）。顺序别反，Validate 是第一道筛子。

- [x] **2c. ✅ 已修：`identity_check` 改用函数内惰性获取 LLM**（2026-10-12 完成并验证）

      [nodes.py:302-308](backend/src/graph/nodes.py#L302-L308) 在**模块导入时**就把 LLM 抓成了一个全局变量：

      ```python
      # LLM服务初始化 - 使用豆包模型
      try:
          llm: BaseChatModel = get_llm_by_type("basic")   # ← 导入期执行一次
      except Exception as e:
          print(f"Warning: Failed to initialize LLM: {e}")
          llm = None                                       # ← 之后**永远**是 None
      ```

      无 key 启动时这次调用抛异常，被吞掉并永久赋值 `None`。而 `identity_check` —— **整条流水线的第一个节点** —— 正是用这个全局变量（第 325 行 `if llm:`、第 346 行 `llm.invoke(...)`）。所以它会静默退化成规则判断。

      对比之下，第 492 / 593 / 979 行的节点是在**函数内部**重新调用 `get_llm_by_type("basic")` 的，能读到最新设置。**结果是同一进程里两套行为**：后面几个节点能用新 key，第一个节点不能。

      > **更正**：本条初稿曾写成「identity_check 会静默降级成规则判断」，这是**错的**。该节点在 `llm` 为空时实际是**抛异常**（`raise Exception("LLM服务不可用，无法进行身份识别")`），异常会被路由到 `error_recovery`。真正能跑到 `task_selector` 的原因是当时已经保存了有效配置、全局 `llm` 不是 `None`。错误的判断已按实际代码更正。

      **已做的修改**：删掉模块级全局 `llm`（全仓确认无任何地方引用它），改为一个惰性 helper：

      ```python
      def _get_basic_llm() -> Optional[BaseChatModel]:
          try:
              return get_llm_by_type("basic")
          except Exception as e:
              print(f"Warning: Failed to initialize LLM: {e}")
              return None
      ```

      `identity_check_command_node` 现在在函数体内调用它，与第 492/593/979 行的其他节点行为一致。

      **验证证据（零成本，未消耗你的 API 额度）**：猴补 `get_llm_by_type` 后直接调用该节点 → 确认函数**在执行时**才被调用（1 次），路由正确 `→ task_selector`，`user_type=professional`。另实测模块级 `llm` 已不存在（`hasattr` 为 False），相关测试仍 **12 passed**。

      → 现在改配置**不需要重启后端**了。
- [ ] **3. 跑通一轮真实对话**：`POST /query/stream` 走一轮普通问答，再走一条会调用工具的 agent 路径。这一步才算真正证明「接入成功」。
- [ ] **4. 记录 provider 差异**。`api_format` 支持 `openai` / `anthropic` / `auto`：
      - `openai`：base_url 一般到 `/v1`
      - `anthropic`：填 SDK base URL（`https://api.anthropic.com`），**不要**带 `/v1/messages`（后端会自动规范化结尾的 `/v1`、`/v1/messages`）
      - 第三方兼容网关 / DeepSeek 这类，用 `openai` 格式换 base_url 和 model 即可

---

## P1 — 前端

- [ ] **5. 修 Next.js 15 的 `params` 类型错误**（`pnpm build` 失败的原因）

      Next 15 把动态路由的 `params` 从对象改成了 `Promise`。`next dev` 不做这层校验，所以开发模式能跑，`next build` 会挂。全仓库需要改的**只有这两个文件**：
      - [src/app/album/[folder]/page.tsx](frontend/src/app/album/%5Bfolder%5D/page.tsx#L6-L12) — `params: { folder: string }`，第 12 行同步取值
      - [src/app/album/[folder]/manage/page.tsx](frontend/src/app/album/%5Bfolder%5D/manage/page.tsx#L3-L4) — 同上

      改法（两个文件一样；`searchParams` 在 Next 15 里同样是 Promise）：
      ```tsx
      // 组件改成 async，参数类型改成 Promise
      export default async function Page({ params }: { params: Promise<{ folder: string }> }) {
        const { folder } = await params
        // ...
      }
      ```
      ⚠️ `[folder]/page.tsx` 里还有 `generateStaticParams()`，说明 `next.config` 开了 `output: 'export'`（静态导出）。改完记得跑一次完整 `pnpm build` 确认静态导出仍能生成 `dist/`。

- [ ] **6. 消掉 CopilotKit 的 hydration 警告**

      报错来自第三方组件 `@copilotkit/react-ui` 的 `PoweredByTag`（"Powered by CopilotKit" 那行水印）：服务端预渲染的 inline style 和客户端算出来的不一致，React 放弃修补该节点。
      **已排除浏览器扩展**——无痕窗口（禁用全部扩展）下依然复现，所以是组件本身 SSR/CSR 不一致。
      按代价从低到高，三选一：
      1. 给 `<CopilotPopup>` 传 `showPoweredBy={false}` —— 已在 `node_modules/@copilotkit/react-ui/dist` 里确认这是真实 prop，默认 `true`。水印没了，问题节点也就没了。
      2. 用 `dynamic(() => import(...), { ssr: false })` 包住 Copilot 组件，让它完全不参与 SSR，也就没有 hydration 可比对的。
      3. 忽略。这只是 dev 模式的 console 噪音（栈里有 `runWithFiberInDEV`，生产构建不打印），代价是那一行水印会整块重渲染一次，不影响功能。
      建议直接选 1。

- [x] **6b. ✅ 已修：删掉 `observabilityHooks`**（2026-10-12 完成）

      控制台提示 `observabilityHooks requires a publicApiKey to function.` 并建议 `1.10.4 → 1.78.0` 升级。

      **不要照着执行那条升级命令。** 根因是 [layout.tsx:97](frontend/src/app/layout.tsx#L97) 给 `<CopilotPopup>` 传了 `observabilityHooks`：这个特性属于 **Copilot Cloud**，必须要 `publicApiKey`。而本项目是自托管、直连自己的 FastAPI 后端，本来就不该有也不需要有这个 key。

      而那段 hooks 里干的事**全是 `console.log`**（加上一段「美国天文事件」的 mock 数据写 localStorage），零功能价值。

      **已做的修改**：删掉了 `layout.tsx` 中整个 `observabilityHooks={{...}}` prop（59 行，含那段 mock 数据）。该 prop 里只有 `console.log`，删除不影响任何功能。`<CopilotPopup>` 其余 prop 原样保留。
      升级到 1.78.0 是解决不了这个问题的——只要还在自托管又传了 `observabilityHooks`，它照样要 key。

      另外那个带 "Help / Debug" 的浮动面板来自 [layout.tsx:69](frontend/src/app/layout.tsx#L69) 的 `showDevConsole={true}`，生产环境应改回 `false`（或去掉）。

---

## P2 — 仓库卫生 / 发布前

- [ ] **7. ⚠️ 密钥泄露风险（复核后已收窄，但仍有一处真实的漏）**

      > **更正**：本条初稿说 `backend/runtime/llm_settings.json` 未受保护，**这是错的**。该目录下已有 [backend/runtime/.gitignore](backend/runtime/.gitignore)，内容是：
      > ```
      > *
      > !.gitignore
      > ```
      > 即忽略 `runtime/` 下的一切，`llm_settings.json` 已被覆盖。初稿的判断已按实际文件更正。

      **仍然存在的漏洞——`backend/.env`**：该文件实际存在，里面存着 `ENCRYPTION_KEY`，但**没有被忽略**。仓库根 `.gitignore` 只写了 `.env.local` / `.env*.local` 这类后缀变体，**不含纯 `.env`**。一旦 `git add .`，加密密钥就会直接进历史。

      建议在 `backend/` 下新建 `.gitignore`（根目录那份用的是 `/node_modules` 这类**根相对**路径，管不到 backend 内部）：
      ```
      .env
      .venv/
      runtime/
      **/__pycache__/
      *.log
      *.db
      ```

      ⚠️ 注意：一旦任何密钥提交进历史，仅删除文件是没用的，必须 `git filter-repo` 改写历史，并**立刻去供应商后台吊销该 key**。

- [ ] **8. 清理当前 git 索引的异常状态**：`git status` 显示 **379 个文件全部处于 staged 删除**状态（等于整个跟踪树被标记为删除），且 `.venv/`（106 个文件）**曾经被提交进仓库**。索引处于半完成状态，别在这个状态下直接 `git commit`。建议先 `git reset` 回到干净状态，补好第 7 条的 `.gitignore`，再重新 `git add`。

- [ ] **9. 生产构建**：
      ```bash
      pnpm --dir frontend build          # 先过第 5 条
      cargo check --manifest-path src-tauri/Cargo.toml
      pnpm --dir frontend tauri build
      ```

- [ ] **10. 确认打包产物能连到生产后端**：`NEXT_PUBLIC_ASTRO_BACKEND_URL` 需指向部署好的后端（本地开发默认 `http://127.0.0.1:8000`）。Tauri 从 `frontend/dist` 读静态导出。

- [ ] **11. 确认 `VALIDATION_REPORT.md` 里「Not verified」那几项在本机补齐**：真实 provider 请求、`pnpm build`、`cargo check`/`tauri build` 当时都因环境缺依赖没跑，属于第一批该在真机上验的。

---

## 已知问题（既有，非本次改动引入）

- [ ] **12. `tests/test_error_handler.py` 第 6 行有个残留的 `ni`**，导致语法错误。pytest 在**收集阶段就整体中断**，所以 `pytest` 现在一个测试都跑不了。删掉那一行即可（看内容像是某次编辑被截断的产物）。修好后 `pytest` 才能正常跑全量。

- [ ] **13. 三个测试文件的既有失败**（已确认与本次修复无关）：
      - `tests/test_enhanced_config.py` — 9 个失败，原因 `LLM API key is required; Secret key is required`，这些测试依赖环境变量里有真实凭据，属环境依赖问题，不是代码 bug。
      - `tests/test_state_manager.py::test_update_state` — 时间戳断言 `assert 1791795454.36 > 1791795454.36`，是同一时刻取值导致的**测试不稳定**，建议改成 `>=` 或给时间戳加一点延迟。

      **参考基线**：`tests/test_llm_protocol_compat.py` + `test_llm_settings_contract.py` + `test_stream_request_compat.py` 三个文件 **12 passed**，与 `VALIDATION_REPORT.md` 记录一致；本次修复后复跑仍为 12 passed。

- [ ] **14. `/serial` 路由是坏的，而且是个死路由**（既有问题）

      `GET /serial` 返回 **307** 并渲染 `__next_error__` 错误页，根因是 `NEXT_REDIRECT`：

      ```tsx
      // src/app/serial/page.tsx —— 全文只有 5 行
      export default function SerialPage() {
        redirect("/home");   // ← 在静态导出（output: 'export'）下不被支持，直接抛错
      }
      ```

      Next.js 的 `redirect()` 在 `output: 'export'` 静态导出模式下无法工作（没有服务端可执行重定向）。而这个路由**全项目零引用**（`grep` 不到任何 `/serial` 链接），所以没人发现它坏了。

      **建议**：既然注释写着「串口功能已移除」，最干净的是**直接删掉整个 `src/app/serial/` 目录**（连带 `SerialManager.tsx`、`serial-manager.tsx`、`head.tsx`），第 15 条的 17 个类型错误也随之消失。若想保留 `/serial` 这个地址避免外部旧链接 404，则改成客户端跳转：
      ```tsx
      "use client";
      import { useEffect } from "react";
      import { useRouter } from "next/navigation";
      export default function SerialPage() {
        const router = useRouter();
        useEffect(() => { router.replace("/home"); }, [router]);
        return null;
      }
      ```
      这是产品决定，没有替你选。

      **补充：这个功能已经彻底下线了，但尸体还留在树上。**`serial` 原本是一个**串口（RS-232）硬件通信控制台**——刷新/自动检测串口、手动连接、实时收发数据、按类型和内容过滤消息。在这套天文 agent 的语境里通常用于控制赤道仪/天文相机/滤镜轮/圆顶这类设备（具体设备协议代码里没写死，属领域推断）。

      现状是全链路皆空：
      - `app/serial/page.tsx` — 6 行，`redirect("/home")`
      - `app/serial/head.tsx` — title 是「已移除的页面」，还加了 `noindex`
      - `hooks/useSerial.ts` — **空壳**，所有方法返回空数组 / no-op，注释「串口功能已移除；保留占位实现以避免历史引用报错」
      - `app/serial/SerialManager.tsx` — 133 行完整 UI，但依赖上面那个空壳，所以整页是死的；且**全项目零引用**
      - 后端无任何串口代码
      - ⚠️ **更正**：初稿写「Tauri 没有串口代码」，**不准确**。`src-tauri/src/serial/` 里其实有一套真实的 Rust 实现（`communication.rs` 15KB、`commands.rs`、`types.rs`、`mod.rs`，共约 20KB）。但它**从未被接线**：
        - `src-tauri/src/lib.rs` 和 `main.rs` **都没有声明 `mod serial;`**，所以这个模块**根本不参与编译**
        - `src-tauri/Cargo.toml` 的依赖里**没有 `serialport`**，即使声明了也编译不过
        - `invoke_handler` 只注册了 `greet` 一个命令
        → 结论不变（功能确实是死的），但性质是「写好了没接线的孤儿代码」，不是「没有代码」。
      - 全项目 grep 不到任何 `/serial` 链接

      另外两个附带发现：
      - `app/serial/serial-manager.tsx` 是 **0 字节空文件**，和 `SerialManager.tsx` 只差大小写。在 Windows 大小写不敏感的文件系统上这俩会互相遮蔽，是个隐患，一并删掉。
      - `SerialManager.tsx` 里有 3 处 `className="flex justify之间 items-center"` —— **中文「之间」串进了 className**（第 58、63、112、123 行一带）。说明这个文件被某次批量替换或复制粘贴弄坏过。

      → 结论：**整个 `src/app/serial/` 目录连同 `src/hooks/useSerial.ts` 一起删掉**最干净，第 15 条的 17 个类型错误也随之消失。

- [ ] **15. `src/app/serial/SerialManager.tsx` 有 17 个 TypeScript 错误**（既有问题）

      全是 `Property 'data' / 'message_type' / 'port_name' / 'timestamp' does not exist on type 'never'` 这类。典型的 `useState` 初始值推断成 `never` 后没给显式泛型：

      ```tsx
      const [messages, setMessages] = useState([]);          // 推断为 never[]
      const [messages, setMessages] = useState<SerialMessage[]>([]);  // ← 需要显式标注
      ```

      （第 36、39 行还有 `Expected 0 arguments, but got 1`，是调用签名不匹配。）若采纳第 14 条直接删目录，这条一并消失。

- [ ] **16. ⚠️ `VALIDATION_REPORT.md` 的 TypeScript 结论偏乐观，别当基线用**

      `VALIDATION_REPORT.md` 写的是 `tsc --project tsconfig.json --noCheck --noEmit`。**`--noCheck` 会跳过类型检查**，只做语法解析——所以上面第 5 条（Next 15 `params`）和第 15 条那 17 个错误当时全都检测不到，报告里的「TypeScript 通过」并不等于类型无误。

      本次实跑 `pnpm exec tsc --noEmit` 的**真实结果：18 个错误**，分布在 3 处：
      - `.next/types/app/album/[folder]/page.ts` 与 `manage/page.ts` —— 2 个，即第 5 条
      - `src/app/serial/SerialManager.tsx` —— 17 个，即第 15 条

      建议把这个命令作为 CI 基线，别再带 `--noCheck`。

---

## 参考：本地启动

```bash
# 后端
cd backend
./.venv/Scripts/python.exe -m uvicorn api_service.main:app --host 0.0.0.0 --port 8000

# 前端（开发模式，绕开第 5 条的类型错误）
cd frontend
pnpm dev        # → http://localhost:3000
```
