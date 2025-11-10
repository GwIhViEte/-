# GitHub Actions 自动打包使用指南

## 🚀 快速开始

### 方法一：自动触发（推荐）
1. **推送代码到主分支**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   git push origin main
   ```

2. **创建版本标签（自动发布）**
   ```bash
   git tag v5.0.0
   git push origin v5.0.0
   ```

### 方法二：手动触发
1. 访问 GitHub 仓库的 **Actions** 页面
2. 选择 **"Multi-Platform Build and Release"** 工作流
3. 点击 **"Run workflow"**
4. 选择构建参数：
   - `build_all`: true（构建所有平台）
   - `python_version`: 3.11（默认Python版本）

## 📦 构建产物下载

### 自动发布（标签推送）
创建标签后会自动：
- ✅ 构建所有平台（Windows、Linux、macOS）
- ✅ 创建 GitHub Release
- ✅ 上传构建产物到 Release

### 手动下载
1. 访问 **Actions** → **构建任务**
2. 在 **Artifacts** 部分下载：
   - `AI_Novel_Generator_windows.zip`（Windows）
   - `AI_Novel_Generator_linux.tar.gz`（Linux）
   - `AI_Novel_Generator_macos.zip`（macOS）

## 💻 本地构建

### Windows
```bash
# 双击运行
build_windows.bat
```

### Linux
```bash
# 给脚本执行权限
chmod +x build_linux.sh

# 运行构建
./build_linux.sh
```

### macOS
```bash
# 给脚本执行权限
chmod +x build_macos.sh

# 运行构建
./build_macos.sh
```

## 🔧 构建配置

### PyInstaller 选项
- **单文件模式**：`--onefile`
- **无控制台**：`--windowed`
- **包含图标**：`--icon=resources/icon.ico`
- **自动包含模块**：所有核心模块和依赖

### 隐式导入处理
自动包含以下模块，避免运行时错误：
- `core.*`（核心功能）
- `utils.*`（工具函数）
- `templates.*`（模板系统）
- `ui.*`（用户界面）
- `tkinter` 相关模块
- `PIL` 相关模块
- `aiohttp`（HTTP客户端）

## 📁 文件结构

### 构建产物包含
```
AI_Novel_Generator/
├── AI_Novel_Generator.exe    # 主程序
├── run.bat                         # Windows启动脚本
├── core/                           # 核心模块
│   ├── __init__.py
│   ├── generator.py
│   ├── media_generator.py
│   └── ...
├── utils/                          # 工具模块
│   ├── __init__.py
│   ├── common.py
│   ├── config.py
│   ├── quality.py                  # 质量评估模块
│   └── ...
├── templates/                       # 模板文件
│   ├── prompts.py
│   └── ...
├── ui/                             # 用户界面
│   ├── __init__.py
│   ├── app.py
│   ├── dialogs.py
│   └── assets/
├── resources/                       # 资源文件
│   └── icon.ico
├── example_prompts/                 # 示例文件
├── main.py                         # 主入口
├── main_wrapper.py                 # 包装器
├── README.md                       # 说明文档
├── README_EN.md                    # 英文文档
└── LICENSE.txt                      # 许可证
```

## 🎯 工作流触发条件

### 自动触发
- ✅ 推送到 `main`、`master`、`develop` 分支
- ✅ 创建版本标签（`v*`）
- ✅ Pull Request 到主分支

### 手动触发
- ✅ GitHub Actions 页面手动运行
- ✅ 可选择特定平台和Python版本
- ✅ 支持批量构建所有平台

## 🔄 持续集成

### 构建矩阵
| 平台 | 运行环境 | Python版本 | 输出格式 |
|------|----------|------------|----------|
| Windows | windows-latest | 3.9-3.12 | ZIP |
| Linux | ubuntu-latest | 3.9-3.12 | TAR.GZ |
| macOS | macos-latest | 3.9-3.12 | ZIP |

### 质量保证
- ✅ 代码语法检查
- ✅ 依赖安装验证
- ✅ 构建成功确认
- ✅ 文件完整性检查
- ✅ 多平台兼容性测试

## 📊 构建信息

每次构建生成 `build_info.txt`：
```
构建信息
=================
构建日期: 2024-11-10
构建时间: 05:34:15
平台: Windows
Python版本: 3.11
Git提交: abc123def
分支: main
版本号: 5.0.0
```

## 🚨 故障排除

### 常见问题
1. **构建失败**：检查 `requirements.txt` 是否完整
2. **图标缺失**：确保 `resources/icon.ico` 存在
3. **模块导入错误**：检查 `hiddenimports` 配置
4. **权限错误**：Linux/macOS 需要执行权限

### 调试方法
1. 查看 Actions 日志获取详细错误信息
2. 本地运行构建脚本进行测试
3. 检查 PyInstaller 版本兼容性

## 🎉 发布流程

### 自动发布（推荐）
```bash
# 1. 更新版本号
vim templates/prompts.py  # 修改 __version__

# 2. 提交代码
git add .
git commit -m "release: v5.0.0"
git push origin main

# 3. 创建标签
git tag v5.0.0
git push origin v5.0.0

# 4. 等待自动构建和发布
```

### 手动发布
1. 运行本地构建脚本
2. 下载构建产物
3. 在 GitHub 创建 Release
4. 上传构建文件

现在你的项目已经完全配置了自动化打包，每次代码更新都会自动生成多平台的可执行文件！