# CI/CD 自动打包配置

已为项目配置了完整的GitHub Actions自动打包流程，支持多平台构建。

## 🚀 自动触发条件

### 推送触发
- 推送到 `main`、`master`、`develop` 分支
- 创建版本标签（如 `v5.0.0`）
- Pull Request 到主分支

### 手动触发
- 在GitHub Actions页面手动运行
- 可选择特定平台和Python版本

## 📦 构建矩阵

### 支持的平台
- **Windows** (Windows Latest)
- **Linux** (Ubuntu Latest) 
- **macOS** (macOS Latest)

### 支持的Python版本
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

## 🔧 构建流程

### 1. 环境准备
- 检出代码
- 设置Python环境
- 安装系统依赖（如Tkinter）
- 安装Python依赖包

### 2. 依赖安装
```bash
pip install pyinstaller
pip install -r requirements.txt
pip install aiohttp pillow  # 额外打包依赖
```

### 3. 可执行文件构建
```bash
# Windows
pyinstaller --onefile --windowed --name "AI_Novel_Generator_v5.0.0" --icon=resources/icon.ico main.py

# Linux  
pyinstaller --onefile --name "AI_Novel_Generator_v5.0.0" main.py

# macOS
pyinstaller --onefile --windowed --name "AI_Novel_Generator_v5.0.0" --icon=resources/icon.icns main.py
```

### 4. 打包内容
- 核心模块 (`core/`)
- 工具模块 (`utils/`)
- 模板文件 (`templates/`)
- UI模块 (`ui/`)
- 资源文件 (`resources/`)
- 示例文件 (`example_prompts/`)
- 文档 (`README*.md`)
- 启动脚本

### 5. 创建发布包
- **Windows**: ZIP格式
- **Linux**: TAR.GZ格式  
- **macOS**: ZIP格式

## 📁 输出文件

### Windows
```
AI_Novel_Generator_v5.0.0_windows.zip
├── AI_Novel_Generator_v5.0.0.exe
├── run.bat                    # 启动脚本
├── core/                      # 核心模块
├── utils/                     # 工具模块
├── templates/                  # 模板文件
├── ui/                        # UI模块
├── resources/                  # 资源文件
├── example_prompts/            # 示例文件
└── README.md                   # 说明文档
```

### Linux
```
AI_Novel_Generator_v5.0.0_linux.tar.gz
├── AI_Novel_Generator_v5.0.0      # 可执行文件
├── run.sh                     # 启动脚本
├── core/                      # 核心模块
├── utils/                     # 工具模块
├── templates/                  # 模板文件
├── ui/                        # UI模块
├── resources/                  # 资源文件
├── example_prompts/            # 示例文件
└── README.md                   # 说明文档
```

### macOS
```
AI_Novel_Generator_v5.0.0_macos.zip
├── AI_Novel_Generator_v5.0.0      # 可执行文件
├── run.command                 # 启动脚本
├── core/                      # 核心模块
├── utils/                     # 工具模块
├── templates/                  # 模板文件
├── ui/                        # UI模块
├── resources/                  # 资源文件
├── example_prompts/            # 示例文件
└── README.md                   # 说明文档
```

## 🎯 使用方法

### 自动构建
1. **推送代码**到主分支即可触发构建
2. **创建标签**（如 `git tag v5.0.0`）会创建GitHub Release
3. **手动触发**在Actions页面选择参数运行

### 下载构建产物
1. 访问项目的 **Actions** 页面
2. 选择最新的构建任务
3. 在 **Artifacts** 部分下载对应平台的压缩包
4. 解压后运行启动脚本

## 🔧 配置说明

### 必需的文件
```
.github/workflows/
├── build-windows.yml    # Windows构建
├── build-linux.yml      # Linux构建  
├── build-macos.yml      # macOS构建
└── build-all.yml        # 多平台构建
```

### PyInstaller配置
- 使用 `--onefile` 生成单文件
- 使用 `--windowed` 隐藏控制台
- 自动包含所有必要的模块和资源

### 版本管理
- 自动从 `templates/prompts.py` 读取版本号
- 构建产物包含版本信息文件
- 支持预发布版本（beta标签）

## 🚨 注意事项

### 图标文件
确保以下图标文件存在：
- `resources/icon.ico` (Windows)
- `resources/icon.icns` (macOS)
- `resources/icon.png` (Linux备用)

### 依赖管理
- `requirements.txt` 应包含所有运行时依赖
- 打包时会额外安装 `aiohttp` 和 `pillow`
- 确保所有隐式导入都被正确处理

### 权限设置
- Linux/macOS启动脚本设置执行权限
- Windows批处理文件保持兼容性
- macOS `.command` 文件可双击执行

## 🔄 持续集成

构建流程包含以下质量检查：
- ✅ 代码语法检查
- ✅ 依赖安装验证
- ✅ 构建成功确认
- ✅ 文件完整性检查
- ✅ 多平台兼容性测试

## 📊 构建统计

每次构建会生成包含以下信息的 `build_info.txt`：
- 构建日期和时间
- 目标平台
- Python版本
- Git提交哈希
- 分支名称
- 软件版本号

## 🎉 发布流程

### 自动发布（标签推送）
1. 推送版本标签：`git tag v5.0.0 && git push origin v5.0.0`
2. GitHub Actions自动：
   - 构建所有平台
   - 创建GitHub Release
   - 上传构建产物
   - 生成发布说明

### 手动发布
1. 在Actions页面手动运行构建
2. 下载Artifacts中的构建产物
3. 手动创建Release并上传文件

这样配置后，每次代码更新都会自动生成多平台的可执行文件，大大简化了分发流程！