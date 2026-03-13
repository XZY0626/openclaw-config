# OpenClaw 操作日志 - 2026-03-13

## 操作摘要
- 操作时间：2026-03-13 20:59
- 操作范围：OpenClaw 前端 model-selector 插件升级 v4→v5

## 变更内容

### model-selector-v2.js 升级 v4 → v5
新增模型分组：**MiniMax**（4个模型）
- `minimax/MiniMax-M1` — 思考型，alias: minimax-m1
- `minimax/MiniMax-M2` — 推理型，alias: minimax-m2  
- `minimax/MiniMax-M2.5` — 旗舰版，alias: minimax
- `minimax/MiniMax-Text-01` — 长文本，alias: minimax-text

## 版本防丢策略
1. npm 包路径：`/usr/lib/node_modules/openclaw/dist/control-ui/assets/model-selector-v2.js`
2. 持久备份：`~/.openclaw/model-selector-v2.js`（VM 用户目录，不受更新影响）
3. 恢复脚本：`~/.openclaw/apply-custom-ui.sh`（运行即可恢复自定义UI）
4. 云端备份：本 GitHub 仓库 `openclaw-frontend/model-selector-v2.js`

## 验证结果
- npm 包文件 MiniMax 行数：6
- HTTP 服务 MiniMax 行数：6
- Security Audit：0 critical · 3 warn

## API Key 说明
- MiniMax API Key 已配置于虚拟机系统环境变量（脱敏，不入库）
- Key 位置：虚拟机 `/etc/environment` 或 `~/.bashrc`

## 相关文件
- `openclaw-frontend/model-selector-v2.js`：前端模型选择器（v5）
- `~/.openclaw/apply-custom-ui.sh`：恢复脚本（VM 上）
